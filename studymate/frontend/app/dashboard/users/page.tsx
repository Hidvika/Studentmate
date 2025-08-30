'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Search, Users, Edit, Eye, Trash2, UserPlus, Shield, UserCheck, UserX } from 'lucide-react';

import { useUsers, useDeleteUser } from '@/hooks/useUsers';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import DashboardLayout from '@/components/DashboardLayout';
import { UsersResponse } from '@/lib/types';

export default function UsersPage() {
  const { user: currentUser } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(10);
  const [filters, setFilters] = useState<Record<string, any>>({});

  // Fetch users using React Query (superuser only)
  const { data: usersData, isLoading, error } = useUsers(
    currentPage,
    pageSize,
    searchQuery || undefined,
    filters
  );

  // Delete user mutation
  const deleteUser = useDeleteUser();

  // Type assertions to ensure proper typing
  const users = (usersData as UsersResponse)?.items || [];
  const total = (usersData as UsersResponse)?.total || 0;
  const totalPages = Math.ceil(total / pageSize);

  // Redirect if not superuser
  if (currentUser && !currentUser.is_superuser) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <Shield className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-red-600 mb-4">Access Denied</h2>
          <p className="text-gray-600">You don't have permission to access this page.</p>
        </div>
      </DashboardLayout>
    );
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
  };

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
  };

  const handleDelete = async (id: string, username: string) => {
    if (id === currentUser?.id) {
      alert('You cannot delete your own account!');
      return;
    }
    
    if (window.confirm(`Are you sure you want to delete user "${username}"? This action cannot be undone.`)) {
      await deleteUser.mutateAsync(id);
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
          <h2 className="text-2xl font-bold text-red-600 mb-4">Error Loading Users</h2>
          <p className="text-gray-600">{error.message || 'Failed to load users'}</p>
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
            <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
            <p className="text-gray-600">Manage all users in the system</p>
          </div>
          <Button asChild>
            <Link href="/dashboard/users/new">
              <UserPlus className="w-4 h-4 mr-2" />
              Add User
            </Link>
          </Button>
        </div>

        {/* Search and Filters */}
        <Card>
          <CardHeader>
            <CardTitle>Search & Filters</CardTitle>
            <CardDescription>Find specific users quickly</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <form onSubmit={handleSearch} className="flex space-x-4">
              <div className="flex-1">
                <Input
                  placeholder="Search users by username or email..."
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
                <span className="text-sm text-gray-600">Status:</span>
                <select
                  className="border rounded px-2 py-1 text-sm"
                  onChange={(e) => handleFilterChange('is_active', e.target.value === 'true' ? true : e.target.value === 'false' ? false : undefined)}
                  value={filters.is_active === true ? 'true' : filters.is_active === false ? 'false' : ''}
                >
                  <option value="">All Status</option>
                  <option value="true">Active</option>
                  <option value="false">Inactive</option>
                </select>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Role:</span>
                <select
                  className="border rounded px-2 py-1 text-sm"
                  onChange={(e) => handleFilterChange('is_superuser', e.target.value === 'true' ? true : e.target.value === 'false' ? false : undefined)}
                  value={filters.is_superuser === true ? 'true' : filters.is_superuser === false ? 'false' : ''}
                >
                  <option value="">All Roles</option>
                  <option value="true">Superuser</option>
                  <option value="false">Regular User</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Users List */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>Users ({total})</CardTitle>
                <CardDescription>
                  {isLoading ? 'Loading...' : `${users.length} of ${total} users`}
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
                <p className="mt-2 text-gray-600">Loading users...</p>
              </div>
            ) : users.length === 0 ? (
              <div className="text-center py-8">
                <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">
                  {searchQuery || Object.keys(filters).length > 0
                    ? 'No users match your search criteria'
                    : 'No users found'}
                </p>
                {!searchQuery && Object.keys(filters).length === 0 && (
                  <Button asChild className="mt-2">
                    <Link href="/dashboard/users/new">
                      Add your first user
                    </Link>
                  </Button>
                )}
              </div>
            ) : (
              <div className="space-y-3">
                {users.map((user) => (
                  <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        {user.is_superuser ? (
                          <Shield className="h-6 w-6 text-purple-600" />
                        ) : (
                          <Users className="h-6 w-6 text-blue-600" />
                        )}
                        <div>
                          <h3 className="font-medium text-lg">{user.username}</h3>
                          <p className="text-sm text-gray-500">{user.email}</p>
                          <div className="flex items-center space-x-2 mt-1">
                            {user.is_active ? (
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                <UserCheck className="h-3 w-3 mr-1" />
                                Active
                              </span>
                            ) : (
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                <UserX className="h-3 w-3 mr-1" />
                                Inactive
                              </span>
                            )}
                            {user.is_superuser && (
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                                <Shield className="h-3 w-3 mr-1" />
                                Superuser
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button variant="ghost" size="sm" asChild>
                        <Link href={`/dashboard/users/${user.id}`}>
                          <Eye className="h-4 w-4" />
                        </Link>
                      </Button>
                      <Button variant="ghost" size="sm" asChild>
                        <Link href={`/dashboard/users/${user.id}/edit`}>
                          <Edit className="h-4 w-4" />
                        </Link>
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(user.id, user.username)}
                        disabled={deleteUser.isPending || user.id === currentUser?.id}
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
