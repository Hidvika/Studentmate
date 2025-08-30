# WebSocket Real-time Chat Implementation in StudyMate

## Overview

This document describes the WebSocket implementation for real-time chat functionality in the StudyMate frontend, which provides instant message delivery, typing indicators, and real-time updates for AI-powered conversations.

## Features

- **Real-time Communication**: Instant message delivery via WebSocket connections
- **Typing Indicators**: Shows when AI is processing responses
- **Connection Status**: Visual indicators for WebSocket connection state
- **Automatic Reconnection**: Handles connection drops gracefully
- **Message Persistence**: All conversations are automatically saved
- **Citation Support**: Real-time display of source citations
- **User Authentication**: Secure WebSocket connections with user authentication

## Architecture

### Frontend Components

#### RealTimeChat Component
The main chat component that handles WebSocket communication:

```tsx
// components/RealTimeChat.tsx
export function RealTimeChat({ chatId, onChatCreated }: RealTimeChatProps) {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  // ... other state
}
```

#### Chat Pages
- **`/dashboard/chats`**: List all user chats
- **`/dashboard/chats/new`**: Start new conversations
- **`/dashboard/chats/[id]`**: View existing conversations

### WebSocket Message Types

#### Authentication Message
```typescript
{
  type: 'auth',
  data: {
    user_id: string;
    chat_id?: string;
  }
}
```

#### Chat Message
```typescript
{
  type: 'message',
  data: {
    message: Message;
    user_id: string;
    chat_id?: string;
  }
}
```

#### Typing Indicator
```typescript
{
  type: 'typing',
  data: {
    user_id: string;
    chat_id?: string;
    is_typing: boolean;
  }
}
```

#### Load Messages Request
```typescript
{
  type: 'load_messages',
  data: {
    chat_id: string;
    user_id: string;
  }
}
```

### Message Interface

```typescript
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
```

## Implementation Details

### WebSocket Connection Management

```tsx
useEffect(() => {
  if (!user) return;

  const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/chat';
  const socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    setIsConnected(true);
    // Send authentication
    socket.send(JSON.stringify({
      type: 'auth',
      data: { user_id: user.id, chat_id: currentChatId }
    }));
  };

  // ... other event handlers

  return () => socket.close();
}, [user, currentChatId, onChatCreated]);
```

### Message Handling

```tsx
socket.onmessage = (event) => {
  try {
    const chatMessage: ChatMessage = JSON.parse(event.data);
    
    switch (chatMessage.type) {
      case 'message':
        if (chatMessage.data.message) {
          setMessages(prev => {
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
        }
        break;
      // ... other cases
    }
  } catch (error) {
    console.error('Error parsing WebSocket message:', error);
  }
};
```

### Typing Indicators

```tsx
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

// Debounced typing indicator
const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
  setInput(e.target.value);
  
  if (typingTimeoutRef.current) {
    clearTimeout(typingTimeoutRef.current);
  }
  
  sendTypingIndicator(true);
  
  typingTimeoutRef.current = setTimeout(() => {
    sendTypingIndicator(false);
  }, 1000);
};
```

## Usage Examples

### Starting a New Chat

```tsx
// app/dashboard/chats/new/page.tsx
export default function NewChatPage() {
  const [chatId, setChatId] = useState<string | undefined>();

  const handleChatCreated = (newChatId: string) => {
    setChatId(newChatId);
  };

  return (
    <DashboardLayout>
      <div className="h-[600px]">
        <RealTimeChat 
          chatId={chatId} 
          onChatCreated={handleChatCreated}
        />
      </div>
    </DashboardLayout>
  );
}
```

### Viewing Existing Chat

```tsx
// app/dashboard/chats/[id]/page.tsx
export default function ChatDetailPage() {
  const params = useParams();
  const chatId = params.id as string;

  return (
    <DashboardLayout>
      <div className="h-[600px]">
        <RealTimeChat chatId={chatId} />
      </div>
    </DashboardLayout>
  );
}
```

## Configuration

### Environment Variables

```bash
# WebSocket URL (optional, defaults to localhost)
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/chat
```

### WebSocket URL Structure

- **Development**: `ws://localhost:8000/ws/chat`
- **Production**: `wss://yourdomain.com/ws/chat`

## Error Handling

### Connection Errors

```tsx
socket.onerror = (error) => {
  console.error('WebSocket error:', error);
  toast.error('Connection error. Please refresh the page.');
};
```

### Message Parsing Errors

```tsx
try {
  const chatMessage: ChatMessage = JSON.parse(event.data);
  // Process message
} catch (error) {
  console.error('Error parsing WebSocket message:', error);
}
```

### Graceful Degradation

- Shows connection status to users
- Disables input when disconnected
- Provides clear error messages
- Automatic reconnection attempts

## Security Considerations

### Authentication

- WebSocket connections require user authentication
- User ID is validated on the server side
- Chat access is restricted to chat owners

### Data Validation

- All incoming messages are validated
- Message types are strictly enforced
- User permissions are checked for each operation

## Performance Optimizations

### Message Deduplication

```tsx
setMessages(prev => {
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
```

### Debounced Typing Indicators

- Typing indicators are debounced to reduce WebSocket traffic
- Automatic cleanup of typing timeouts
- Efficient state updates

### Connection Management

- Single WebSocket connection per user
- Automatic cleanup on component unmount
- Connection state monitoring

## Future Enhancements

### Planned Features

1. **Message Encryption**: End-to-end encryption for sensitive conversations
2. **File Sharing**: Real-time file upload and sharing
3. **Voice Messages**: Audio message support
4. **Group Chats**: Multi-user conversation support
5. **Message Reactions**: Emoji reactions to messages
6. **Read Receipts**: Message read status indicators

### Technical Improvements

1. **Connection Pooling**: Multiple WebSocket connections for load balancing
2. **Message Queuing**: Offline message queuing and delivery
3. **Compression**: Message compression for large conversations
4. **Caching**: Intelligent message caching strategies
5. **Analytics**: Chat usage analytics and insights

## Troubleshooting

### Common Issues

1. **Connection Failures**
   - Check WebSocket URL configuration
   - Verify server is running and accessible
   - Check network connectivity

2. **Message Not Received**
   - Verify WebSocket connection status
   - Check message format and validation
   - Review server-side logs

3. **Typing Indicators Not Working**
   - Check typing timeout configuration
   - Verify WebSocket message format
   - Review client-side event handling

### Debug Mode

Enable debug logging by setting:

```typescript
// In development
console.log('WebSocket connected');
console.log('WebSocket message:', event.data);
console.log('WebSocket error:', error);
```

## Best Practices

1. **Connection Management**
   - Always close WebSocket connections on unmount
   - Handle connection state changes gracefully
   - Implement automatic reconnection logic

2. **Message Handling**
   - Validate all incoming messages
   - Handle message parsing errors gracefully
   - Implement message deduplication

3. **User Experience**
   - Show clear connection status
   - Provide meaningful error messages
   - Implement loading states and indicators

4. **Performance**
   - Debounce frequent operations (typing indicators)
   - Optimize state updates
   - Clean up timeouts and intervals

## Conclusion

The WebSocket implementation provides a robust foundation for real-time chat functionality in StudyMate. It offers instant communication, typing indicators, and seamless user experience while maintaining security and performance standards.

The modular architecture allows for easy extension and maintenance, making it simple to add new features like file sharing, voice messages, and group chats in the future.
