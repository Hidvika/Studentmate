'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Plus, Search, MessageCircle, Edit, Eye, Trash2, Filter, MoreHorizontal } from 'lucide-react';

import { useUserChats, useDeleteChat } from '@/hooks/useChats';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import DashboardLayout from '@/components/DashboardLayout';
import { ChatsResponse } from '@/lib/types';

export default function ChatsPage() {
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(10);
  const [filters, setFilters] = useState<Record<string, any>>({});

  // Fetch user's chats using React Query
  const { data: chatsData, isLoading, error } = useUserChats(
    user?.id || '',
    currentPage,
    pageSize
  );

  // Delete chat mutation
  const deleteChat = useDeleteChat();

  // Type assertions to ensure proper typing
  const chats = (chatsData as ChatsResponse)?.items || [];
  const total = (chatsData as ChatsResponse)?.total || 0;
  const totalPages = Math.ceil(total / pageSize);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
  };

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this chat? This action cannot be undone.')) {
      await deleteChat.mutateAsync(id);
    }
  };

  const handleFilterChange = (key: string, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
    setCurrentPage(1);
  };

  if (error) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Error Loading Chats</h2>
          <p className="text-gray-600">{error.message || 'Failed to load chats'}</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Chats</h1>
            <p className="text-gray-600">Your conversations with AI</p>
          </div>
          <Button asChild>
            <Link href="/dashboard/chats/new">
              <Plus className="w-4 h-4 mr-2" />
              New Chat
            </Link>
          </Button>
        </div>

        {/* Search and Filters */}
        <Card>
          <CardHeader>
            <CardTitle>Search & Filters</CardTitle>
            <CardDescription>Find specific conversations quickly</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <form onSubmit={handleSearch} className="flex space-x-4">
              <div className="flex-1">
                <Input
                  placeholder="Search chats by title..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full"
                />
              </div>
              <Button type="submit">
                <Search className="w-4 h-4 mr-2" />
                Search
              </Button>
            </form>

            <div className="flex space-x-4">
              <div className="flex items-center space-x-2">
                <Filter className="h-4 w-4 text-gray-500" />
                <span className="text-sm text-gray-600">Date Range:</span>
                <select
                  className="border rounded px-2 py-1 text-sm"
                  onChange={(e) => handleFilterChange('date_range', e.target.value || undefined)}
                  value={filters.date_range || ''}
                >
                  <option value="">All Time</option>
                  <option value="today">Today</option>
                  <option value="week">This Week</option>
                  <option value="month">This Month</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Chats List */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>Chats ({total})</CardTitle>
                <CardDescription>
                  {isLoading ? 'Loading...' : `${chats.length} of ${total} chats`}
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
                <p className="mt-2 text-gray-600">Loading chats...</p>
              </div>
            ) : chats.length === 0 ? (
              <div className="text-center py-8">
                <MessageCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">
                  {searchQuery || Object.keys(filters).length > 0
                    ? 'No chats match your search criteria'
                    : 'No chats yet'}
                </p>
                {!searchQuery && Object.keys(filters).length === 0 && (
                  <Button asChild className="mt-2">
                    <Link href="/dashboard/chats/new">
                      Start your first chat
                    </Link>
                  </Button>
                )}
              </div>
            ) : (
              <div className="space-y-3">
                {chats.map((chat) => (
                  <div key={chat.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                    <div className="flex items-center space-x-4">
                      <MessageCircle className="h-8 w-8 text-green-600" />
                      <div>
                        <h3 className="font-medium text-lg">{chat.title}</h3>
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <span>Created {new Date(chat.created_at).toLocaleDateString()}</span>
                          <span>Updated {new Date(chat.updated_at).toLocaleDateString()}</span>
                        </div>
                        {chat.metadata && (
                          <p className="text-gray-600 mt-1 text-sm">
                            {Object.keys(chat.metadata).length} metadata fields
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button variant="ghost" size="sm" asChild>
                        <Link href={`/dashboard/chats/${chat.id}`}>
                          <Eye className="h-4 w-4" />
                        </Link>
                      </Button>
                      <Button variant="ghost" size="sm" asChild>
                        <Link href={`/dashboard/chats/${chat.id}/edit`}>
                          <Edit className="h-4 w-4" />
                        </Link>
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(chat.id)}
                        disabled={deleteChat.isPending}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex justify-center space-x-2">
            <Button
              variant="outline"
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
            >
              Previous
            </Button>
            
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              let pageNum;
              if (totalPages <= 5) {
                pageNum = i + 1;
              } else if (currentPage <= 3) {
                pageNum = i + 1;
              } else if (currentPage >= totalPages - 2) {
                pageNum = totalPages - 4 + i;
              } else {
                pageNum = currentPage - 2 + i;
              }
              
              return (
                <Button
                  key={pageNum}
                  variant={currentPage === pageNum ? "default" : "outline"}
                  onClick={() => handlePageChange(pageNum)}
                  size="sm"
                >
                  {pageNum}
                </Button>
              );
            })}
            
            <Button
              variant="outline"
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage >= totalPages}
            >
              Next
            </Button>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
