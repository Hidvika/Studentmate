'use client';

import React, { useState } from 'react';
import { Plus, Search, FileText, Upload, Users, MessageCircle, Trash2, Edit, Eye } from 'lucide-react';
import Link from 'next/link';

import { useAuth } from '@/contexts/AuthContext';
import { useDocuments } from '@/hooks/useDocuments';
import { useUserChats } from '@/hooks/useChats';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { DocumentsResponse, ChatsResponse } from '@/lib/types';

export default function DashboardPage() {
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(10);

  // Fetch documents using React Query
  const { data: documentsData, isLoading: documentsLoading, error: documentsError } = useDocuments(
    currentPage,
    pageSize,
    searchQuery || undefined
  );

  // Fetch user's chats using React Query
  const { data: chatsData, isLoading: chatsLoading, error: chatsError } = useUserChats(
    user?.id || '',
    currentPage,
    pageSize
  );

  // Type assertions to ensure proper typing
  const documents = (documentsData as DocumentsResponse)?.items || [];
  const chats = (chatsData as ChatsResponse)?.items || [];
  const totalDocuments = (documentsData as DocumentsResponse)?.total || 0;
  const totalChats = (chatsData as ChatsResponse)?.total || 0;

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1); // Reset to first page when searching
  };

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
  };

  if (documentsError || chatsError) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Error Loading Dashboard</h2>
          <p className="text-gray-600">
            {documentsError?.message || chatsError?.message || 'Failed to load dashboard data'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Welcome back, {user?.username}!</p>
        </div>
        <div className="flex space-x-3">
          <Button asChild>
            <Link href="/dashboard/documents/new">
              <Plus className="w-4 h-4 mr-2" />
              New Document
            </Link>
          </Button>
          <Button asChild variant="outline">
            <Link href="/dashboard/chats/new">
              <MessageCircle className="w-4 h-4 mr-2" />
              New Chat
            </Link>
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <form onSubmit={handleSearch} className="flex space-x-4">
        <div className="flex-1">
          <Input
            placeholder="Search documents..."
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

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {documentsLoading ? '...' : totalDocuments}
            </div>
            <p className="text-xs text-muted-foreground">
              {documentsLoading ? 'Loading...' : 'Documents in your library'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Chats</CardTitle>
            <MessageCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {chatsLoading ? '...' : totalChats}
            </div>
            <p className="text-xs text-muted-foreground">
              {chatsLoading ? 'Loading...' : 'Conversations with AI'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Storage Used</CardTitle>
            <Upload className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2.4 GB</div>
            <p className="text-xs text-muted-foreground">
              of 10 GB available
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Documents */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Recent Documents</CardTitle>
              <CardDescription>Your recently uploaded documents</CardDescription>
            </div>
            <Button asChild variant="outline" size="sm">
              <Link href="/dashboard/documents">
                View All
              </Link>
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {documentsLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading documents...</p>
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No documents yet</p>
              <Button asChild className="mt-2">
                <Link href="/dashboard/documents/new">
                  Upload your first document
                </Link>
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {documents.slice(0, 5).map((doc) => (
                <div key={doc.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                  <div className="flex items-center space-x-3">
                    <FileText className="h-5 w-5 text-blue-600" />
                    <div>
                      <p className="font-medium">{doc.title}</p>
                      <p className="text-sm text-gray-500">
                        {new Date(doc.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <Button variant="ghost" size="sm" asChild>
                      <Link href={`/dashboard/documents/${doc.id}`}>
                        <Eye className="h-4 w-4" />
                      </Link>
                    </Button>
                    <Button variant="ghost" size="sm" asChild>
                      <Link href={`/dashboard/documents/${doc.id}/edit`}>
                        <Edit className="h-4 w-4" />
                      </Link>
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent Chats */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Recent Chats</CardTitle>
              <CardDescription>Your recent conversations with AI</CardDescription>
            </div>
            <Button asChild variant="outline" size="sm">
              <Link href="/dashboard/chats">
                View All
              </Link>
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {chatsLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading chats...</p>
            </div>
          ) : chats.length === 0 ? (
            <div className="text-center py-8">
              <MessageCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No chats yet</p>
              <Button asChild className="mt-2">
                <Link href="/dashboard/chats/new">
                  Start your first chat
                </Link>
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {chats.slice(0, 5).map((chat) => (
                <div key={chat.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                  <div className="flex items-center space-x-3">
                    <MessageCircle className="h-5 w-5 text-green-600" />
                    <div>
                      <p className="font-medium">{chat.title}</p>
                      <p className="text-sm text-gray-500">
                        {new Date(chat.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex space-x-2">
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
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      {totalDocuments > pageSize && (
        <div className="flex justify-center space-x-2">
          <Button
            variant="outline"
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
          >
            Previous
          </Button>
          <span className="flex items-center px-3 py-2 text-sm">
            Page {currentPage} of {Math.ceil(totalDocuments / pageSize)}
          </span>
          <Button
            variant="outline"
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage >= Math.ceil(totalDocuments / pageSize)}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
