import { useState, useCallback } from 'react';
import { Upload, FileCode, CheckCircle, AlertCircle, X } from 'lucide-react';
import { apiService } from '../services/api';
import type { UploadResponse } from '../types';

interface FileUploaderProps {
  onUploadSuccess?: () => void;
}

export default function FileUploader({ onUploadSuccess }: FileUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<UploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      await uploadFile(files[0]);
    }
  }, []);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      await uploadFile(files[0]);
    }
  };

  const uploadFile = async (file: File) => {
    setUploading(true);
    setError(null);
    setResult(null);

    try {
      const response = await apiService.uploadFile(file);
      setResult(response);
      onUploadSuccess?.();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload file');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Your Code</h2>
        <p className="text-gray-600">
          Upload code files to analyze and chat about them
        </p>
      </div>

      {/* Drag & Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          relative border-2 border-dashed rounded-lg p-12 transition-all
          ${isDragging
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-gray-400'
          }
          ${uploading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
      >
        <input
          type="file"
          onChange={handleFileSelect}
          accept=".py,.js,.jsx,.ts,.tsx,.java,.cpp,.go,.rs"
          disabled={uploading}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />

        <div className="flex flex-col items-center space-y-4">
          <div className="bg-primary-100 p-4 rounded-full">
            {uploading ? (
              <div className="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
            ) : (
              <Upload className="w-12 h-12 text-primary-600" />
            )}
          </div>

          <div className="text-center">
            <p className="text-lg font-medium text-gray-900">
              {uploading ? 'Uploading...' : 'Drop your code file here'}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              or click to browse
            </p>
          </div>

          <div className="flex flex-wrap gap-2 justify-center text-xs text-gray-500">
            <span className="bg-gray-100 px-2 py-1 rounded">.py</span>
            <span className="bg-gray-100 px-2 py-1 rounded">.js</span>
            <span className="bg-gray-100 px-2 py-1 rounded">.ts</span>
            <span className="bg-gray-100 px-2 py-1 rounded">.java</span>
            <span className="bg-gray-100 px-2 py-1 rounded">.cpp</span>
            <span className="bg-gray-100 px-2 py-1 rounded">.go</span>
            <span className="bg-gray-100 px-2 py-1 rounded">.rs</span>
          </div>
        </div>
      </div>

      {/* Success Message */}
      {result && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-medium text-green-900">Upload Successful!</h3>
              <div className="mt-2 text-sm text-green-800 space-y-1">
                <p>
                  <span className="font-medium">File:</span> {result.file_name}
                </p>
                <p>
                  <span className="font-medium">Language:</span> {result.language}
                </p>
                <p>
                  <span className="font-medium">Chunks created:</span> {result.chunks_created}
                </p>
              </div>
              <p className="mt-2 text-sm text-green-700">{result.message}</p>
            </div>
            <button
              onClick={() => setResult(null)}
              className="text-green-600 hover:text-green-800"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-medium text-red-900">Upload Failed</h3>
              <p className="mt-1 text-sm text-red-700">{error}</p>
            </div>
            <button
              onClick={() => setError(null)}
              className="text-red-600 hover:text-red-800"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <FileCode className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-medium text-blue-900 mb-2">How it works:</h3>
            <ol className="list-decimal list-inside space-y-1 text-sm text-blue-800">
              <li>Upload your code file (Python, JavaScript, TypeScript, etc.)</li>
              <li>The system parses and chunks your code into meaningful segments</li>
              <li>Each chunk is converted to embeddings (vectors)</li>
              <li>Embeddings are stored in the vector database for semantic search</li>
              <li>Now you can chat about your code!</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}
