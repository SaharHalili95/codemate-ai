export interface CodeChunk {
  id: string;
  file_name: string;
  content: string;
  language: string;
  line_start: number;
  line_end: number;
  metadata?: Record<string, any>;
}

export interface SearchResult {
  chunk: CodeChunk;
  score: number;
  distance?: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources?: CodeChunk[];
  timestamp?: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  include_history?: boolean;
}

export interface ChatResponse {
  message: string;
  sources: CodeChunk[];
  conversation_id: string;
  model_used: string;
  tokens_used?: number;
}

export interface UploadResponse {
  success: boolean;
  file_name: string;
  chunks_created: number;
  language: string;
  message: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  llm_provider: string;
  vector_db: string;
  total_chunks: number;
}

export interface Stats {
  total_chunks: number;
  languages: Record<string, number>;
  files: number;
  collection_name: string;
}
