import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { toast } from 'react-hot-toast';
import { 
  User, UserCreate, UserUpdate, 
  Document, DocumentCreate, DocumentUpdate,
  Chat, ChatCreate, ChatUpdate,
  Message, MessageCreate, MessageUpdate,
  PaginatedResponse
} from '@/lib/types';

// API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Enable cookies
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    // Get token from localStorage (or cookie if you prefer)
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors and token refresh
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      // Clear invalid token
      localStorage.removeItem('auth_token');
      
      // Redirect to login
      if (typeof window !== 'undefined') {
        window.location.href = '/auth/login';
      }
      
      toast.error('Session expired. Please login again.');
    }

    // Handle other errors
    if (error.response?.data?.detail) {
      toast.error(error.response.data.detail);
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    } else if (error.response?.status >= 400) {
      toast.error('Request failed. Please check your input.');
    }

    return Promise.reject(error);
  }
);

// Auth API methods
export const authAPI = {
  register: async (userData: { username: string; email: string; password: string }) => {
    const response = await apiClient.post('/auth/register', userData);
    return response.data;
  },

  login: async (credentials: { username: string; password: string }) => {
    const response = await apiClient.post('/auth/login-json', credentials);
    const { access_token } = response.data;
    
    // Store token
    localStorage.setItem('auth_token', access_token);
    
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('auth_token');
    if (typeof window !== 'undefined') {
      window.location.href = '/auth/login';
    }
  },

  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },
};

// CRUD API methods
export const crudAPI = {
  // Users
  getUsers: async (
    page: number = 1, 
    limit: number = 10, 
    search?: string, 
    filters?: Record<string, any>
  ): Promise<PaginatedResponse<User>> => {
    const params: any = {
      page,
      limit,
      ...(search && { q: search }),
      ...filters
    };
    const response = await apiClient.get('/crud/users', { params });
    return response.data;
  },

  getUser: async (id: string): Promise<User> => {
    const response = await apiClient.get(`/crud/users/${id}`);
    return response.data;
  },

  createUser: async (userData: UserCreate): Promise<User> => {
    const response = await apiClient.post('/crud/users', userData);
    return response.data;
  },

  updateUser: async (id: string, userData: UserUpdate): Promise<User> => {
    const response = await apiClient.put(`/crud/users/${id}`, userData);
    return response.data;
  },

  deleteUser: async (id: string): Promise<User> => {
    const response = await apiClient.delete(`/crud/users/${id}`);
    return response.data;
  },

  // Documents
  getDocuments: async (
    page: number = 1, 
    limit: number = 10, 
    search?: string, 
    filters?: Record<string, any>
  ): Promise<PaginatedResponse<Document>> => {
    const params: any = {
      page,
      limit,
      ...(search && { q: search }),
      ...filters
    };
    const response = await apiClient.get('/crud/documents', { params });
    return response.data;
  },

  getDocument: async (id: string): Promise<Document> => {
    const response = await apiClient.get(`/crud/documents/${id}`);
    return response.data;
  },

  createDocument: async (documentData: DocumentCreate): Promise<Document> => {
    const response = await apiClient.post('/crud/documents', documentData);
    return response.data;
  },

  updateDocument: async (id: string, documentData: DocumentUpdate): Promise<Document> => {
    const response = await apiClient.put(`/crud/documents/${id}`, documentData);
    return response.data;
  },

  deleteDocument: async (id: string): Promise<Document> => {
    const response = await apiClient.delete(`/crud/documents/${id}`);
    return response.data;
  },

  // Chats
  getChats: async (
    page: number = 1, 
    limit: number = 10, 
    search?: string, 
    filters?: Record<string, any>
  ): Promise<PaginatedResponse<Chat>> => {
    const params: any = {
      page,
      limit,
      ...(search && { q: search }),
      ...filters
    };
    const response = await apiClient.get('/crud/chats', { params });
    return response.data;
  },

  getChat: async (id: string): Promise<Chat> => {
    const response = await apiClient.get(`/crud/chats/${id}`);
    return response.data;
  },

  createChat: async (chatData: ChatCreate): Promise<Chat> => {
    const response = await apiClient.post('/crud/chats', chatData);
    return response.data;
  },

  updateChat: async (id: string, chatData: ChatUpdate): Promise<Chat> => {
    const response = await apiClient.put(`/crud/chats/${id}`, chatData);
    return response.data;
  },

  deleteChat: async (id: string): Promise<Chat> => {
    const response = await apiClient.delete(`/crud/chats/${id}`);
    return response.data;
  },

  // Messages
  getMessages: async (
    page: number = 1, 
    limit: number = 10, 
    search?: string, 
    filters?: Record<string, any>
  ): Promise<PaginatedResponse<Message>> => {
    const params: any = {
      page,
      limit,
      ...(search && { q: search }),
      ...filters
    };
    const response = await apiClient.get('/crud/messages', { params });
    return response.data;
  },

  getMessage: async (id: string): Promise<Message> => {
    const response = await apiClient.get(`/crud/messages/${id}`);
    return response.data;
  },

  createMessage: async (messageData: MessageCreate): Promise<Message> => {
    const response = await apiClient.post('/crud/messages', messageData);
    return response.data;
  },

  updateMessage: async (id: string, messageData: MessageUpdate): Promise<Message> => {
    const response = await apiClient.put(`/crud/messages/${id}`, messageData);
    return response.data;
  },

  deleteMessage: async (id: string): Promise<Message> => {
    const response = await apiClient.delete(`/crud/messages/${id}`);
    return response.data;
  },
};

export default apiClient;
