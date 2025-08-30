'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { FileText, Upload, ArrowLeft } from 'lucide-react';

import { useCreateDocument } from '@/hooks/useDocuments';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import DashboardLayout from '@/components/DashboardLayout';
import { DocumentCreate } from '@/lib/types';

export default function NewDocumentPage() {
  const router = useRouter();
  const [isUploading, setIsUploading] = useState(false);
  
  const createDocument = useCreateDocument();
  
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    setValue,
    watch,
  } = useForm<DocumentCreate>({
    mode: 'onChange',
    defaultValues: {
      title: '',
      content: '',
      file_type: '',
      file_size: 0,
    },
  });

  const watchedTitle = watch('title');
  const watchedContent = watch('content');

  const onSubmit = async (data: DocumentCreate) => {
    try {
      await createDocument.mutateAsync(data);
      router.push('/dashboard/documents');
    } catch (error) {
      // Error is handled by the mutation hook
      console.error('Failed to create document:', error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    
    try {
      // Read file content
      const text = await file.text();
      
      // Set form values
      setValue('title', file.name.replace(/\.[^/.]+$/, '')); // Remove extension
      setValue('content', text);
      setValue('file_type', file.name.split('.').pop()?.toLowerCase() || '');
      setValue('file_size', file.size);
      
    } catch (error) {
      console.error('Error reading file:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleManualInput = () => {
    setValue('title', '');
    setValue('content', '');
    setValue('file_type', '');
    setValue('file_size', 0);
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
            <h1 className="text-3xl font-bold text-gray-900">Upload Document</h1>
            <p className="text-gray-600">Add a new document to your library</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* File Upload */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Upload className="w-5 h-5" />
                <span>File Upload</span>
              </CardTitle>
              <CardDescription>
                Upload a file to automatically extract content and metadata
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
                <input
                  type="file"
                  accept=".pdf,.docx,.txt,.md"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="file-upload"
                  disabled={isUploading}
                />
                <label
                  htmlFor="file-upload"
                  className="cursor-pointer flex flex-col items-center space-y-2"
                >
                  <Upload className="h-12 w-12 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {isUploading ? 'Processing...' : 'Click to upload'}
                    </p>
                    <p className="text-xs text-gray-500">
                      PDF, DOCX, TXT, or Markdown files
                    </p>
                  </div>
                </label>
              </div>
              
              <Button
                variant="outline"
                onClick={handleManualInput}
                className="w-full"
                disabled={isUploading}
              >
                <FileText className="w-4 h-4 mr-2" />
                Enter Manually Instead
              </Button>
            </CardContent>
          </Card>

          {/* Document Form */}
          <Card>
            <CardHeader>
              <CardTitle>Document Details</CardTitle>
              <CardDescription>
                Fill in the document information
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div>
                  <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                    Title *
                  </label>
                  <Input
                    id="title"
                    {...register('title', {
                      required: 'Title is required',
                      minLength: {
                        value: 3,
                        message: 'Title must be at least 3 characters',
                      },
                    })}
                    placeholder="Enter document title"
                    className={errors.title ? 'border-red-500' : ''}
                  />
                  {errors.title && (
                    <p className="text-red-500 text-sm mt-1">{errors.title.message}</p>
                  )}
                </div>

                <div>
                  <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-1">
                    Content *
                  </label>
                  <Textarea
                    id="content"
                    {...register('content', {
                      required: 'Content is required',
                      minLength: {
                        value: 10,
                        message: 'Content must be at least 10 characters',
                      },
                    })}
                    placeholder="Enter document content or paste text here"
                    rows={8}
                    className={errors.content ? 'border-red-500' : ''}
                  />
                  {errors.content && (
                    <p className="text-red-500 text-sm mt-1">{errors.content.message}</p>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="file_type" className="block text-sm font-medium text-gray-700 mb-1">
                      File Type
                    </label>
                    <Input
                      id="file_type"
                      {...register('file_type')}
                      placeholder="e.g., pdf, docx"
                      disabled
                    />
                  </div>
                  <div>
                    <label htmlFor="file_size" className="block text-sm font-medium text-gray-700 mb-1">
                      File Size (bytes)
                    </label>
                    <Input
                      id="file_size"
                      {...register('file_size', { valueAsNumber: true })}
                      type="number"
                      disabled
                    />
                  </div>
                </div>

                <div className="flex space-x-3 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => router.push('/dashboard/documents')}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={!isValid || createDocument.isPending}
                    className="flex-1"
                  >
                    {createDocument.isPending ? 'Creating...' : 'Create Document'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Preview */}
        {(watchedTitle || watchedContent) && (
          <Card>
            <CardHeader>
              <CardTitle>Preview</CardTitle>
              <CardDescription>How your document will appear</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {watchedTitle && (
                  <div>
                    <h3 className="font-medium text-gray-900">Title</h3>
                    <p className="text-gray-600">{watchedTitle}</p>
                  </div>
                )}
                {watchedContent && (
                  <div>
                    <h3 className="font-medium text-gray-900">Content Preview</h3>
                    <p className="text-gray-600 line-clamp-3">
                      {watchedContent}
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
