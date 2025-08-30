# React Query Implementation in StudyMate Frontend

## Overview

This document describes the React Query implementation in the StudyMate frontend, which provides efficient data fetching, caching, and state management for the application.

## Features

- **Automatic Caching**: Data is cached and automatically synchronized across components
- **Background Updates**: Data is refreshed in the background when needed
- **Optimistic Updates**: UI updates immediately while mutations are processed
- **Error Handling**: Centralized error handling with toast notifications
- **Loading States**: Built-in loading states for better UX
- **Pagination Support**: Efficient pagination with proper cache management
- **Search & Filtering**: Real-time search and filtering with debounced queries

## Architecture

### QueryProvider

The `QueryProvider` wraps the entire application and provides the React Query context:

```tsx
// contexts/QueryProvider.tsx
export function QueryProvider({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

### Custom Hooks

#### Documents

```tsx
// hooks/useDocuments.ts
export function useDocuments(
  page: number = 1,
  limit: number = 10,
  search?: string,
  filters?: Record<string, any>
) {
  return useQuery({
    queryKey: documentKeys.list({ page, limit, search, filters }),
    queryFn: () => crudAPI.getDocuments(page, limit, search, filters),
    keepPreviousData: true,
  });
}

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
```

#### Chats

```tsx
// hooks/useChats.ts
export function useUserChats(
  userId: string,
  page: number = 1,
  limit: number = 10
) {
  return useQuery({
    queryKey: chatKeys.userChats(userId),
    queryFn: () => crudAPI.getChats(page, limit, undefined, { user_id: userId }),
    enabled: !!userId,
    keepPreviousData: true,
  });
}
```

#### Users

```tsx
// hooks/useUsers.ts
export function useUsers(
  page: number = 1,
  limit: number = 10,
  search?: string,
  filters?: Record<string, any>
) {
  return useQuery({
    queryKey: userKeys.list({ page, limit, search, filters }),
    queryFn: () => crudAPI.getUsers(page, limit, search, filters),
    keepPreviousData: true,
  });
}
```

## Usage Examples

### Basic Data Fetching

```tsx
function DocumentsList() {
  const { data, isLoading, error } = useDocuments(1, 10);
  
  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return (
    <div>
      {data?.items.map(doc => (
        <DocumentCard key={doc.id} document={doc} />
      ))}
    </div>
  );
}
```

### Creating Data

```tsx
function CreateDocument() {
  const createDocument = useCreateDocument();
  
  const handleSubmit = async (data: DocumentCreate) => {
    try {
      await createDocument.mutateAsync(data);
      // Success toast is shown automatically
      // Cache is invalidated automatically
    } catch (error) {
      // Error toast is shown automatically
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {/* form fields */}
      <button disabled={createDocument.isPending}>
        {createDocument.isPending ? 'Creating...' : 'Create'}
      </button>
    </form>
  );
}
```

### Search and Pagination

```tsx
function SearchableDocuments() {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  
  const { data, isLoading } = useDocuments(page, 10, search);
  
  const handleSearch = (query: string) => {
    setSearch(query);
    setPage(1); // Reset to first page
  };
  
  return (
    <div>
      <SearchInput onSearch={handleSearch} />
      <DocumentsList data={data} />
      <Pagination 
        currentPage={page}
        totalPages={Math.ceil((data?.total || 0) / 10)}
        onPageChange={setPage}
      />
    </div>
  );
}
```

## Query Keys

Query keys are structured hierarchically for efficient cache invalidation:

```tsx
export const documentKeys = {
  all: ['documents'] as const,
  lists: () => [...documentKeys.all, 'list'] as const,
  list: (filters: any) => [...documentKeys.lists(), filters] as const,
  details: () => [...documentKeys.all, 'detail'] as const,
  detail: (id: string) => [...documentKeys.details(), id] as const,
};
```

## Cache Invalidation

When mutations succeed, related queries are automatically invalidated:

```tsx
export function useCreateDocument() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: DocumentCreate) => crudAPI.createDocument(data),
    onSuccess: () => {
      // Invalidate all document lists
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
      toast.success('Document created successfully');
    },
  });
}
```

## Configuration

The QueryClient is configured with sensible defaults:

```tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors
        if (error?.response?.status >= 400 && error?.response?.status < 500) {
          return false;
        }
        return failureCount < 3;
      },
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: false,
    },
  },
});
```

## Benefits

1. **Performance**: Automatic caching reduces unnecessary API calls
2. **User Experience**: Immediate UI updates with optimistic rendering
3. **Data Consistency**: Automatic synchronization across components
4. **Error Handling**: Centralized error handling with user-friendly messages
5. **Developer Experience**: Simple hooks API with TypeScript support
6. **Debugging**: React Query DevTools for development

## Best Practices

1. **Use Query Keys**: Always use structured query keys for proper cache management
2. **Handle Loading States**: Show loading indicators for better UX
3. **Error Boundaries**: Implement error boundaries for graceful error handling
4. **Optimistic Updates**: Use optimistic updates for immediate feedback
5. **Cache Invalidation**: Properly invalidate related queries after mutations
6. **TypeScript**: Use proper types for better development experience

## Troubleshooting

### Common Issues

1. **Stale Data**: Ensure proper cache invalidation after mutations
2. **Infinite Loops**: Check query dependencies and enabled conditions
3. **Memory Leaks**: Use proper cleanup in useEffect hooks
4. **Type Errors**: Ensure proper TypeScript types for API responses

### Debugging

Use React Query DevTools to inspect:
- Query states
- Cache contents
- Query invalidation
- Performance metrics

## Future Enhancements

1. **Real-time Updates**: WebSocket integration for live data
2. **Offline Support**: Service worker integration for offline functionality
3. **Advanced Caching**: Redis-like caching strategies
4. **Background Sync**: Automatic data synchronization
5. **Query Prefetching**: Preload data for better performance
