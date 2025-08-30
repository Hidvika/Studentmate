'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, MessageCircle } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import DashboardLayout from '@/components/DashboardLayout';
import { RealTimeChat } from '@/components/RealTimeChat';

export default function NewChatPage() {
  const router = useRouter();
  const [chatId, setChatId] = useState<string | undefined>();

  const handleChatCreated = (newChatId: string) => {
    setChatId(newChatId);
    // Optionally redirect to the chat view
    // router.push(`/dashboard/chats/${newChatId}`);
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="sm" onClick={() => router.back()}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">New Chat</h1>
            <p className="text-gray-600">Start a new conversation with AI</p>
          </div>
        </div>

        {/* Chat Instructions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <MessageCircle className="w-5 h-5" />
              <span>Getting Started</span>
            </CardTitle>
            <CardDescription>
              Ask questions about your documents and get instant AI-powered responses
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm text-gray-600">
              <p>• Ask specific questions about your uploaded documents</p>
              <p>• Get real-time responses with source citations</p>
              <p>• View typing indicators and connection status</p>
              <p>• All conversations are automatically saved</p>
            </div>
          </CardContent>
        </Card>

        {/* Real-time Chat Component */}
        <div className="h-[600px]">
          <RealTimeChat 
            chatId={chatId} 
            onChatCreated={handleChatCreated}
          />
        </div>
      </div>
    </DashboardLayout>
  );
}
