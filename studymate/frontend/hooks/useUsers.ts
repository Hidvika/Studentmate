import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { crudAPI } from '@/lib/api-client';
import { UserCreate, UserUpdate, UsersResponse, UserResponse } from '@/lib/types';

// Query keys
export const userKeys = {
  all: ['users'] as const,
  lists: () => [...userKeys.all, 'list'] as const,
  list: (filters: any) => [...userKeys.lists(), filters] as const,
  details: () => [...userKeys.all, 'detail'] as const,
  detail: (id: string) => [...userKeys.details(), id] as const,
};

// Fetch users with pagination and search (superuser only)
export function useUsers(
  page: number = 1,
  limit: number = 10,
  search?: string,
  filters?: Record<string, any>
) {
  return useQuery<UsersResponse>({
    queryKey: userKeys.list({ page, limit, search, filters }),
    queryFn: () => crudAPI.getUsers(page, limit, search, filters),
    placeholderData: (previousData) => previousData,
  });
}

// Fetch single user
export function useUser(id: string) {
  return useQuery<UserResponse>({
    queryKey: userKeys.detail(id),
    queryFn: () => crudAPI.getUser(id),
    enabled: !!id,
  });
}

// Create user (superuser only)
export function useCreateUser() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: UserCreate) => crudAPI.createUser(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
      toast.success('User created successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create user');
    },
  });
}

// Update user (superuser only)
export function useUpdateUser() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UserUpdate }) =>
      crudAPI.updateUser(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: userKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
      toast.success('User updated successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update user');
    },
  });
}

// Delete user (superuser only)
export function useDeleteUser() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (id: string) => crudAPI.deleteUser(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
      toast.success('User deleted successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete user');
    },
  });
}
