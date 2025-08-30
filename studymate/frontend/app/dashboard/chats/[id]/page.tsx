'use client';

import React from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, MessageCircle, Edit, Trash2 } from 'lucide-react';
import Link from 'next/link';

import { useChat, useDeleteChat } from '@/hooks/useChats';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import DashboardLayout from '@/components/DashboardLayout';
import { RealTimeChat } from '@/components/RealTimeChat';

export default function ChatDetailPage() {
  const params = useParams();
  const router = useRouter();
  const chatId = params.id as string;

  // Fetch chat details using React Query
  const { data: chat, isLoading, error } = useChat(chatId);
  const deleteChat = useDeleteChat();

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this chat? This action cannot be undone.')) {
      try {
        await deleteChat.mutateAsync(chatId);
        router.push('/dashboard/chats');
      } catch (error) {
        console.error('Failed to delete chat:', error);
      }
    }
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading chat...</p>
        </div>
      </DashboardLayout>
    );
  }

  if (error || !chat) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Chat Not Found</h2>
          <p className="text-gray-600">The chat you're looking for doesn't exist or you don't have access to it.</p>
          <Button 
            onClick={() => router.push('/dashboard/chats')} 
            className="mt-4"
          >
            Back to Chats
          </Button>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="sm" onClick={() => router.back()}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{chat.title}</h1>
              <p className="text-gray-600">Chat conversation</p>
            </div>
          </div>
          <div className="flex space-x-2">
            <Button variant="outline" size="sm" asChild>
              <Link href={`/dashboard/chats/${chatId}/edit`}>
                <Edit className="w-4 h-4 mr-2" />
                Edit
              </Link>
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleDelete}
              disabled={deleteChat.isPending}
              className="text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete
            </Button>
          </div>
        </div>

        {/* Chat Info */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <MessageCircle className="w-5 h-5" />
              <span>Chat Information</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium text-gray-700">Created:</span>
                <p className="text-gray-600">{new Date(chat.created_at).toLocaleString()}</p>
              </div>
              <div>
                <span className="font-medium text-gray-700">Last Updated:</span>
                <p className="text-gray-600">{new Date(chat.updated_at).toLocaleString()}</p>
              </div>
              {chat.metadata && Object.keys(chat.metadata).length > 0 && (
                <div className="col-span-2">
                  <span className="font-medium text-gray-700">Metadata:</span>
                  <div className="mt-1 p-2 bg-gray-50 rounded text-xs">
                    <pre className="whitespace-pre-wrap">{JSON.stringify(chat.metadata, null, 2)}</pre>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Real-time Chat Component */}
        <div className="h-[600px]">
          <RealTimeChat chatId={chatId} />
        </div>
      </div>
    </DashboardLayout>
  );
}
