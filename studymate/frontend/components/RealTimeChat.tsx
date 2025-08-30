'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Bot, User, FileText, MessageCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { SourceChip } from './SourceChip';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'react-hot-toast';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: CitationResponse[];
  timestamp: Date;
  chat_id?: string;
}

interface CitationResponse {
  document_id: string;
  chunk_id: string;
  filename: string;
  page_start: number;
  page_end: number;
  score: number;
}

interface ChatMessage {
  type: 'message' | 'typing' | 'error';
  data: {
    message?: Message;
    chat_id?: string;
    user_id?: string;
    is_typing?: boolean;
    error?: string;
  };
}

interface RealTimeChatProps {
  chatId?: string;
  onChatCreated?: (chatId: string) => void;
}

export function RealTimeChat({ chatId, onChatCreated }: RealTimeChatProps) {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentChatId, setCurrentChatId] = useState<string | undefined>(chatId);
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize WebSocket connection
  useEffect(() => {
    if (!user) return;

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/chat';
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
      
      // Send authentication
      socket.send(JSON.stringify({
        type: 'auth',
        data: {
          user_id: user.id,
          chat_id: currentChatId
        }
      }));
    };

    socket.onmessage = (event) => {
      try {
        const chatMessage: ChatMessage = JSON.parse(event.data);
        
        switch (chatMessage.type) {
          case 'message':
            if (chatMessage.data.message) {
              setMessages(prev => {
                // Check if message already exists
                const exists = prev.find(msg => msg.id === chatMessage.data.message!.id);
                if (exists) {
                  return prev.map(msg => 
                    msg.id === chatMessage.data.message!.id 
                      ? { ...msg, ...chatMessage.data.message }
                      : msg
                  );
                } else {
                  return [...prev, chatMessage.data.message!];
                }
              });
              
              // Update chat ID if this is a new chat
              if (chatMessage.data.chat_id && !currentChatId) {
                setCurrentChatId(chatMessage.data.chat_id);
                onChatCreated?.(chatMessage.data.chat_id);
              }
            }
            break;
            
          case 'typing':
            setIsTyping(chatMessage.data.is_typing || false);
            break;
            
          case 'error':
            if (chatMessage.data.error) {
              toast.error(chatMessage.data.error);
            }
            break;
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    socket.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      toast.error('Connection error. Please refresh the page.');
    };

    setWs(socket);

    return () => {
      socket.close();
    };
  }, [user, currentChatId, onChatCreated]);

  // Send typing indicator
  const sendTypingIndicator = useCallback((isTyping: boolean) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'typing',
        data: {
          user_id: user?.id,
          chat_id: currentChatId,
          is_typing: isTyping
        }
      }));
    }
  }, [ws, user?.id, currentChatId]);

  // Handle input changes with typing indicator
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    
    // Clear existing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    
    // Send typing indicator
    sendTypingIndicator(true);
    
    // Stop typing indicator after 1 second of no input
    typingTimeoutRef.current = setTimeout(() => {
      sendTypingIndicator(false);
    }, 1000);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading || !ws || ws.readyState !== WebSocket.OPEN) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
      chat_id: currentChatId
    };

    // Add user message to local state
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    
    // Stop typing indicator
    sendTypingIndicator(false);
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    try {
      // Send message via WebSocket
      ws.send(JSON.stringify({
        type: 'message',
        data: {
          message: userMessage,
          user_id: user?.id,
          chat_id: currentChatId
        }
      }));

      // Create assistant message placeholder
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        chat_id: currentChatId
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message. Please try again.');
      setIsLoading(false);
    }
  };

  // Load existing messages when chat ID changes
  useEffect(() => {
    if (currentChatId && ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'load_messages',
        data: {
          chat_id: currentChatId,
          user_id: user?.id
        }
      }));
    }
  }, [currentChatId, ws, user?.id]);

  return (
    <div className="flex flex-col h-full">
      <Card className="flex-1 flex flex-col">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageCircle className="h-5 w-5" />
            Real-time Chat
            {isConnected ? (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Connected
              </span>
            ) : (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                Disconnected
              </span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col">
          <div className="flex-1 overflow-y-auto space-y-4 mb-4">
            {messages.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <MessageCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Start a conversation by asking a question about your documents.</p>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`flex gap-3 max-w-[80%] ${
                      message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                    }`}
                  >
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                        message.role === 'user'
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-200 text-gray-700'
                      }`}
                    >
                      {message.role === 'user' ? (
                        <User className="h-4 w-4" />
                      ) : (
                        <Bot className="h-4 w-4" />
                      )}
                    </div>
                    <div
                      className={`rounded-lg p-3 ${
                        message.role === 'user'
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      <div className="whitespace-pre-wrap">{message.content}</div>
                      {message.citations && message.citations.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-gray-200">
                          <p className="text-xs text-gray-500 mb-2">Sources:</p>
                          <div className="flex flex-wrap gap-1">
                            {message.citations.map((citation, index) => (
                              <SourceChip
                                key={index}
                                citation={citation}
                                className="text-xs"
                              />
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
            
            {/* Typing indicator */}
            {isTyping && (
              <div className="flex gap-3 justify-start">
                <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-700 flex items-center justify-center flex-shrink-0">
                  <Bot className="h-4 w-4" />
                </div>
                <div className="bg-gray-100 text-gray-900 rounded-lg p-3">
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm text-gray-500">AI is typing...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} className="flex gap-2">
            <Textarea
              value={input}
              onChange={handleInputChange}
              placeholder="Ask a question about your documents..."
              className="flex-1 resize-none"
              rows={1}
              disabled={isLoading || !isConnected}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
            />
            <Button 
              type="submit" 
              disabled={isLoading || !isConnected || !input.trim()}
              size="icon"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
