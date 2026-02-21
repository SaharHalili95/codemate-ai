// Client-side storage for code chunks using localStorage

export interface CodeFile {
  id: string;
  fileName: string;
  content: string;
  uploadedAt: number;
  language: string;
}

export interface CodeChunk {
  id: string;
  fileId: string;
  fileName: string;
  content: string;
  language: string;
  lineStart: number;
  lineEnd: number;
}

const STORAGE_KEY = 'codemate-files';

export const clientStorage = {
  // Get all files
  getFiles(): CodeFile[] {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  },

  // Add a new file
  addFile(file: File): Promise<CodeFile> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = (e) => {
        const content = e.target?.result as string;
        const files = this.getFiles();

        const newFile: CodeFile = {
          id: Date.now().toString(),
          fileName: file.name,
          content,
          uploadedAt: Date.now(),
          language: this.detectLanguage(file.name),
        };

        files.push(newFile);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(files));
        resolve(newFile);
      };

      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsText(file);
    });
  },

  // Delete a file
  deleteFile(fileName: string): void {
    const files = this.getFiles().filter(f => f.fileName !== fileName);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(files));
  },

  // Get all chunks from all files
  getAllChunks(): CodeChunk[] {
    const files = this.getFiles();
    const chunks: CodeChunk[] = [];

    files.forEach(file => {
      const fileChunks = this.chunkFile(file);
      chunks.push(...fileChunks);
    });

    return chunks;
  },

  // Chunk a file into smaller pieces
  chunkFile(file: CodeFile, chunkSize: number = 50): CodeChunk[] {
    const lines = file.content.split('\n');
    const chunks: CodeChunk[] = [];

    for (let i = 0; i < lines.length; i += chunkSize) {
      const chunkLines = lines.slice(i, i + chunkSize);
      const chunk: CodeChunk = {
        id: `${file.id}-chunk-${i}`,
        fileId: file.id,
        fileName: file.fileName,
        content: chunkLines.join('\n'),
        language: file.language,
        lineStart: i + 1,
        lineEnd: Math.min(i + chunkSize, lines.length),
      };
      chunks.push(chunk);
    }

    return chunks;
  },

  // Simple text search (no vector embeddings)
  search(query: string, topK: number = 5): CodeChunk[] {
    const chunks = this.getAllChunks();
    const queryLower = query.toLowerCase();

    // Score chunks based on keyword matches
    const scored = chunks.map(chunk => {
      const contentLower = chunk.content.toLowerCase();
      const matches = (contentLower.match(new RegExp(queryLower, 'g')) || []).length;
      return { chunk, score: matches };
    });

    // Sort by score and return top K
    return scored
      .filter(item => item.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, topK)
      .map(item => item.chunk);
  },

  // Detect programming language from file extension
  detectLanguage(fileName: string): string {
    const ext = fileName.split('.').pop()?.toLowerCase();
    const langMap: Record<string, string> = {
      'py': 'python',
      'js': 'javascript',
      'ts': 'typescript',
      'tsx': 'typescript',
      'jsx': 'javascript',
      'java': 'java',
      'cpp': 'cpp',
      'c': 'c',
      'go': 'go',
      'rs': 'rust',
      'rb': 'ruby',
      'php': 'php',
      'cs': 'csharp',
    };
    return langMap[ext || ''] || 'text';
  },

  // Get stats
  getStats() {
    const files = this.getFiles();
    const chunks = this.getAllChunks();

    const languageCounts: Record<string, number> = {};
    files.forEach(file => {
      languageCounts[file.language] = (languageCounts[file.language] || 0) + 1;
    });

    return {
      totalFiles: files.length,
      totalChunks: chunks.length,
      languages: languageCounts,
    };
  },

  // Clear all data
  clear(): void {
    localStorage.removeItem(STORAGE_KEY);
  },
};
