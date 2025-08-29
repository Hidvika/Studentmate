const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'

export interface SearchRequest {
  query: string
  k?: number
}

export interface SearchHit {
  chunk_id: string
  document_id: string
  filename: string
  page_start: number
  page_end: number
  text: string
  score: number
  chunk_index: number
}

export interface SearchResponse {
  hits: SearchHit[]
  total_hits: number
  query: string
}

export interface ChatRequest {
  query: string
  chat_id?: string
  top_k?: number
}

export interface CitationResponse {
  document_id: string
  chunk_id: string
  filename: string
  page_start: number
  page_end: number
  score: number
}

export interface ChatResponse {
  chat_id: string
  message_id: string
  answer: string
  citations: CitationResponse[]
}

export interface IngestionResponse {
  document_ids: string[]
  status: string
}

export interface IngestionStatusResponse {
  status: string
  stats: {
    pages: number
    chunks: number
  }
}

class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'APIError'
  }
}

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new APIError(response.status, errorText)
  }

  return response.json()
}

export const api = {
  // Search
  search: (request: SearchRequest): Promise<SearchResponse> =>
    apiRequest('/search', {
      method: 'POST',
      body: JSON.stringify(request),
    }),

  // Chat
  chat: (request: ChatRequest): Promise<ChatResponse> =>
    apiRequest('/chat', {
      method: 'POST',
      body: JSON.stringify(request),
    }),

  chatStream: (request: ChatRequest): EventSource => {
    const url = `${API_BASE}/chat/stream`
    const params = new URLSearchParams()
    params.append('query', request.query)
    if (request.chat_id) params.append('chat_id', request.chat_id)
    if (request.top_k) params.append('top_k', request.top_k.toString())

    return new EventSource(`${url}?${params.toString()}`)
  },

  getChat: (chatId: string): Promise<any> =>
    apiRequest(`/chat/${chatId}`),

  // Ingestion
  uploadDocuments: (files: File[]): Promise<IngestionResponse> => {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))

    return fetch(`${API_BASE}/ingest`, {
      method: 'POST',
      body: formData,
    }).then(response => {
      if (!response.ok) {
        throw new APIError(response.status, 'Upload failed')
      }
      return response.json()
    })
  },

  getIngestionStatus: (documentId: string): Promise<IngestionStatusResponse> =>
    apiRequest(`/ingest/${documentId}/status`),

  deleteDocument: (documentId: string): Promise<void> =>
    apiRequest(`/ingest/${documentId}`, { method: 'DELETE' }),

  // Search stats
  getSearchStats: (): Promise<any> =>
    apiRequest('/search/stats'),
}
