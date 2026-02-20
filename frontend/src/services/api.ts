import axios from 'axios';
import type {
  ChatRequest,
  ChatResponse,
  UploadResponse,
  HealthResponse,
  Stats,
  SearchResult
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Health check
  async getHealth(): Promise<HealthResponse> {
    const response = await api.get('/');
    return response.data;
  },

  // Upload code file
  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Chat with the assistant
  async chat(request: ChatRequest): Promise<ChatResponse> {
    const response = await api.post('/chat', request);
    return response.data;
  },

  // Search code semantically
  async search(query: string, topK: number = 5): Promise<{ results: SearchResult[]; total: number; query: string }> {
    const response = await api.post('/search', {
      query,
      top_k: topK,
    });
    return response.data;
  },

  // Delete file
  async deleteFile(fileName: string): Promise<{ success: boolean; chunks_deleted: number }> {
    const response = await api.delete(`/files/${fileName}`);
    return response.data;
  },

  // Get stats
  async getStats(): Promise<Stats> {
    const response = await api.get('/stats');
    return response.data;
  },
};
