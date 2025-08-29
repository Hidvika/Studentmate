'use client'

import React, { useState } from 'react'
import { Upload, MessageCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { FileDrop } from '@/components/FileDrop'
import { Chat } from '@/components/Chat'

export default function Home() {
  const [activeTab, setActiveTab] = useState<'upload' | 'chat'>('upload')

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">StudyMate</h1>
            <p className="text-lg text-gray-600">
              Upload your documents and chat with an AI assistant
            </p>
          </div>

          <div className="flex justify-center mb-6">
            <div className="flex bg-white rounded-lg p-1 shadow-sm">
              <Button
                variant={activeTab === 'upload' ? 'default' : 'ghost'}
                onClick={() => setActiveTab('upload')}
                className="flex items-center gap-2"
              >
                <Upload className="h-4 w-4" />
                Upload Documents
              </Button>
              <Button
                variant={activeTab === 'chat' ? 'default' : 'ghost'}
                onClick={() => setActiveTab('chat')}
                className="flex items-center gap-2"
              >
                <MessageCircle className="h-4 w-4" />
                Chat
              </Button>
            </div>
          </div>

          <div className="space-y-6">
            {activeTab === 'upload' && (
              <FileDrop />
            )}
            
            {activeTab === 'chat' && (
              <div className="h-[600px]">
                <Chat />
              </div>
            )}
          </div>

          <div className="mt-12 text-center text-sm text-gray-500">
            <p>StudyMate - AI-powered document analysis and chat</p>
          </div>
        </div>
      </div>
    </div>
  )
}


