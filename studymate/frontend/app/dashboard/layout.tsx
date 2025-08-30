'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { LogOut, User, FileText, MessageCircle, Settings } from 'lucide-react';

import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, logout } = useAuth();
  const router = useRouter();

  // Redirect to login if not authenticated
  React.useEffect(() => {
    if (!user) {
      router.push('/auth/login');
    }
  }, [user, router]);

  if (!user) {
    return null; // Don't render anything while redirecting
  }

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Link href="/dashboard" className="text-xl font-bold text-gray-900">
                StudyMate
              </Link>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <User className="h-4 w-4 text-gray-500" />
                <span className="text-sm text-gray-700">{user.username}</span>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleLogout}
                className="flex items-center space-x-2"
              >
                <LogOut className="h-4 w-4" />
                <span>Logout</span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-white shadow-sm min-h-screen">
          <nav className="mt-8">
            <div className="px-4 space-y-2">
              <Link
                href="/dashboard"
                className="flex items-center space-x-3 px-3 py-2 text-gray-700 rounded-md hover:bg-gray-100 hover:text-gray-900"
              >
                <FileText className="h-5 w-5" />
                <span>Documents</span>
              </Link>
              
              <Link
                href="/dashboard/chats"
                className="flex items-center space-x-3 px-3 py-2 text-gray-700 rounded-md hover:bg-gray-100 hover:text-gray-900"
              >
                <MessageCircle className="h-5 w-5" />
                <span>Chats</span>
              </Link>
              
              {user.is_superuser && (
                <Link
                  href="/dashboard/users"
                  className="flex items-center space-x-3 px-3 py-2 text-gray-700 rounded-md hover:bg-gray-100 hover:text-gray-900"
                >
                  <User className="h-5 w-5" />
                  <span>Users</span>
                </Link>
              )}
              
              <Link
                href="/dashboard/settings"
                className="flex items-center space-x-3 px-3 py-2 text-gray-700 rounded-md hover:bg-gray-100 hover:text-gray-900"
              >
                <Settings className="h-5 w-5" />
                <span>Settings</span>
              </Link>
            </div>
          </nav>
        </aside>

        {/* Main content */}
        <main className="flex-1 p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
