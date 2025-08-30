import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { crudAPI } from '@/lib/api-client';
import { DocumentCreate, DocumentUpdate, DocumentsResponse, DocumentResponse } from '@/lib/types';

// Query keys
export const documentKeys = {
  all: ['documents'] as const,
  lists: () => [...documentKeys.all, 'list'] as const,
  list: (filters: any) => [...documentKeys.lists(), filters] as const,
  details: () => [...documentKeys.all, 'detail'] as const,
  detail: (id: string) => [...documentKeys.details(), id] as const,
};

// Fetch documents with pagination and search
export function useDocuments(
  page: number = 1,
  limit: number = 10,
  search?: string,
  filters?: Record<string, any>
) {
  return useQuery<DocumentsResponse>({
    queryKey: documentKeys.list({ page, limit, search, filters }),
    queryFn: () => crudAPI.getDocuments(page, limit, search, filters),
    placeholderData: (previousData) => previousData,
  });
}

// Fetch single document
export function useDocument(id: string) {
  return useQuery<DocumentResponse>({
    queryKey: documentKeys.detail(id),
    queryFn: () => crudAPI.getDocument(id),
    enabled: !!id,
  });
}

// Create document
export function useCreateDocument() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: DocumentCreate) => crudAPI.createDocument(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
      toast.success('Document created successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create document');
    },
  });
}

// Update document
export function useUpdateDocument() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: DocumentUpdate }) =>
      crudAPI.updateDocument(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: documentKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
      toast.success('Document updated successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update document');
    },
  });
}

// Delete document
export function useDeleteDocument() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => crudAPI.deleteDocument(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
      toast.success('Document deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete document');
    },
  });
}
