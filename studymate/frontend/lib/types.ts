// Base types
export interface BaseEntity {
  id: string;
  created_at: string;
  updated_at: string;
}

// User types
export interface User extends BaseEntity {
  email: string;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
}

export interface UserCreate {
  email: string;
  username: string;
  password: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

export interface UserUpdate {
  email?: string;
  username?: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

// Document types
export interface Document extends BaseEntity {
  title: string;
  content: string;
  file_path?: string;
  file_type?: string;
  file_size?: number;
  metadata?: Record<string, any>;
}

export interface DocumentCreate {
  title: string;
  content: string;
  file_path?: string;
  file_type?: string;
  file_size?: number;
  metadata?: Record<string, any>;
}

export interface DocumentUpdate {
  title?: string;
  content?: string;
  file_path?: string;
  file_type?: string;
  file_size?: number;
  metadata?: Record<string, any>;
}

// Chat types
export interface Chat extends BaseEntity {
  title: string;
  user_id: string;
  metadata?: Record<string, any>;
}

export interface ChatCreate {
  title: string;
  user_id: string;
  metadata?: Record<string, any>;
}

export interface ChatUpdate {
  title?: string;
  metadata?: Record<string, any>;
}

// Message types
export interface Message extends BaseEntity {
  content: string;
  role: 'user' | 'assistant';
  chat_id: string;
  metadata?: Record<string, any>;
}

export interface MessageCreate {
  content: string;
  role: 'user' | 'assistant';
  chat_id: string;
  metadata?: Record<string, any>;
}

export interface MessageUpdate {
  content?: string;
  role?: 'user' | 'assistant';
  metadata?: Record<string, any>;
}

// Citation types
export interface Citation extends BaseEntity {
  content: string;
  source: string;
  page_number?: number;
  message_id: string;
  metadata?: Record<string, any>;
}

export interface CitationCreate {
  content: string;
  source: string;
  page_number?: number;
  message_id: string;
  metadata?: Record<string, any>;
}

export interface CitationUpdate {
  content?: string;
  source?: string;
  page_number?: number;
  metadata?: Record<string, any>;
}

// Pagination types
export interface PaginationParams {
  page: number;
  limit: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

// Search types
export interface SearchParams {
  search?: string;
  filters?: Record<string, any>;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

// React Query specific types
export type DocumentsResponse = PaginatedResponse<Document>;
export type ChatsResponse = PaginatedResponse<Chat>;
export type UsersResponse = PaginatedResponse<User>;
export type DocumentResponse = Document;
export type ChatResponse = Chat;
export type UserResponse = User;
