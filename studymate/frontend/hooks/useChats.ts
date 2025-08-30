import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { crudAPI } from '@/lib/api-client';
import { ChatCreate, ChatUpdate, ChatsResponse, ChatResponse } from '@/lib/types';

// Query keys
export const chatKeys = {
  all: ['chats'] as const,
  lists: () => [...chatKeys.all, 'list'] as const,
  list: (filters: any) => [...chatKeys.lists(), filters] as const,
  details: () => [...chatKeys.all, 'detail'] as const,
  detail: (id: string) => [...chatKeys.details(), id] as const,
  userChats: (userId: string) => [...chatKeys.all, 'user', userId] as const,
};

// Fetch chats with pagination and search
export function useChats(
  page: number = 1,
  limit: number = 10,
  search?: string,
  filters?: Record<string, any>
) {
  return useQuery<ChatsResponse>({
    queryKey: chatKeys.list({ page, limit, search, filters }),
    queryFn: () => crudAPI.getChats(page, limit, search, filters),
    placeholderData: (previousData) => previousData,
  });
}

// Fetch user's chats
export function useUserChats(
  userId: string,
  page: number = 1,
  limit: number = 10
) {
  return useQuery<ChatsResponse>({
    queryKey: chatKeys.userChats(userId),
    queryFn: () => crudAPI.getChats(page, limit, undefined, { user_id: userId }),
    enabled: !!userId,
    placeholderData: (previousData) => previousData,
  });
}

// Fetch single chat
export function useChat(id: string) {
  return useQuery<ChatResponse>({
    queryKey: chatKeys.detail(id),
    queryFn: () => crudAPI.getChat(id),
    enabled: !!id,
  });
}

// Create chat
export function useCreateChat() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: ChatCreate) => crudAPI.createChat(data),
    onSuccess: (chat) => {
      queryClient.invalidateQueries({ queryKey: chatKeys.lists() });
      if (chat.user_id) {
        queryClient.invalidateQueries({ queryKey: chatKeys.userChats(chat.user_id) });
      }
      toast.success('Chat created successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create chat');
    },
  });
}

// Update chat
export function useUpdateChat() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ChatUpdate }) =>
      crudAPI.updateChat(id, data),
    onSuccess: (chat, { id }) => {
      queryClient.invalidateQueries({ queryKey: chatKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: chatKeys.lists() });
      if (chat.user_id) {
        queryClient.invalidateQueries({ queryKey: chatKeys.userChats(chat.user_id) });
      }
      toast.success('Chat updated successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update chat');
    },
  });
}

// Delete chat
export function useDeleteChat() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => crudAPI.deleteChat(id),
    onSuccess: (chat) => {
      queryClient.invalidateQueries({ queryKey: chatKeys.lists() });
      if (chat.user_id) {
        queryClient.invalidateQueries({ queryKey: chatKeys.userChats(chat.user_id) });
      }
      toast.success('Chat deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete chat');
    },
  });
}
