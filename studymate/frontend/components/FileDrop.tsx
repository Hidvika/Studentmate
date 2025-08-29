'use client'

import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { api, IngestionResponse } from '@/lib/api'

interface FileStatus {
  file: File
  status: 'uploading' | 'processing' | 'completed' | 'error'
  documentId?: string
  error?: string
  progress?: number
}

interface FileDropProps {
  onUploadComplete?: (response: IngestionResponse) => void
}

export function FileDrop({ onUploadComplete }: FileDropProps) {
  const [fileStatuses, setFileStatuses] = useState<FileStatus[]>([])

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const pdfFiles = acceptedFiles.filter(file => file.type === 'application/pdf')
    
    if (pdfFiles.length === 0) {
      alert('Please select PDF files only')
      return
    }

    // Initialize file statuses
    const newFileStatuses: FileStatus[] = pdfFiles.map(file => ({
      file,
      status: 'uploading'
    }))
    setFileStatuses(prev => [...prev, ...newFileStatuses])

    try {
      // Upload files
      const response = await api.uploadDocuments(pdfFiles)
      
      // Update statuses to processing
      setFileStatuses(prev => prev.map(status => {
        if (pdfFiles.includes(status.file)) {
          return { ...status, status: 'processing' as const }
        }
        return status
      }))

      // Poll for completion
      const pollInterval = setInterval(async () => {
        const allCompleted = await Promise.all(
          response.document_ids.map(async (documentId, index) => {
            try {
              const statusResponse = await api.getIngestionStatus(documentId)
              
              setFileStatuses(prev => prev.map(status => {
                if (status.file === pdfFiles[index]) {
                  return {
                    ...status,
                    status: statusResponse.status === 'indexed' ? 'completed' : 'processing',
                    documentId
                  }
                }
                return status
              }))

              return statusResponse.status === 'indexed'
            } catch (error) {
              setFileStatuses(prev => prev.map(status => {
                if (status.file === pdfFiles[index]) {
                  return {
                    ...status,
                    status: 'error' as const,
                    error: 'Failed to check status'
                  }
                }
                return status
              }))
              return true // Stop polling for this file
            }
          })
        )

        if (allCompleted.every(Boolean)) {
          clearInterval(pollInterval)
          onUploadComplete?.(response)
        }
      }, 2000)

      // Clear interval after 5 minutes to prevent infinite polling
      setTimeout(() => clearInterval(pollInterval), 5 * 60 * 1000)

    } catch (error) {
      console.error('Upload failed:', error)
      setFileStatuses(prev => prev.map(status => {
        if (pdfFiles.includes(status.file)) {
          return {
            ...status,
            status: 'error' as const,
            error: error instanceof Error ? error.message : 'Upload failed'
          }
        }
        return status
      }))
    }
  }, [onUploadComplete])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: true
  })

  const removeFile = (fileToRemove: File) => {
    setFileStatuses(prev => prev.filter(status => status.file !== fileToRemove))
  }

  const getStatusIcon = (status: FileStatus['status']) => {
    switch (status) {
      case 'uploading':
        return <Upload className="h-4 w-4 animate-pulse" />
      case 'processing':
        return <FileText className="h-4 w-4 animate-spin" />
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />
    }
  }

  const getStatusText = (status: FileStatus['status']) => {
    switch (status) {
      case 'uploading':
        return 'Uploading...'
      case 'processing':
        return 'Processing...'
      case 'completed':
        return 'Completed'
      case 'error':
        return 'Error'
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Upload Documents</CardTitle>
          <CardDescription>
            Drag and drop PDF files here or click to browse
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
              ${isDragActive 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-300 hover:border-gray-400'
              }
            `}
          >
            <input {...getInputProps()} />
            <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-lg font-medium text-gray-900 mb-2">
              {isDragActive ? 'Drop files here' : 'Upload PDF documents'}
            </p>
            <p className="text-sm text-gray-500">
              Support for multiple PDF files
            </p>
          </div>
        </CardContent>
      </Card>

      {fileStatuses.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Upload Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {fileStatuses.map((fileStatus, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(fileStatus.status)}
                    <div>
                      <p className="font-medium">{fileStatus.file.name}</p>
                      <p className="text-sm text-gray-500">
                        {getStatusText(fileStatus.status)}
                        {fileStatus.error && ` - ${fileStatus.error}`}
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(fileStatus.file)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
