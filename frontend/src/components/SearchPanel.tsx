import { useState } from 'react';
import { Search, FileCode } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { apiService } from '../services/api';
import type { SearchResult } from '../types';

export default function SearchPanel() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setSearched(true);

    try {
      const response = await apiService.search(query, 5);
      setResults(response.results);
    } catch (error) {
      console.error('Search failed:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Semantic Code Search</h2>
        <p className="text-gray-600">
          Search for code by meaning, not just keywords
        </p>
      </div>

      {/* Search Input */}
      <div className="flex space-x-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="e.g., 'authentication logic', 'database connection', 'error handling'..."
            className="input-field pl-10"
          />
        </div>
        <button
          onClick={handleSearch}
          disabled={loading || !query.trim()}
          className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {/* Results */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : searched && results.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <FileCode className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p className="text-lg font-medium">No results found</p>
          <p className="text-sm mt-2">Try a different query or upload more code</p>
        </div>
      ) : results.length > 0 ? (
        <div className="space-y-4">
          <div className="text-sm text-gray-600">
            Found <span className="font-medium">{results.length}</span> results
          </div>

          {results.map((result, index) => (
            <div key={index} className="bg-white rounded-lg shadow-md p-6">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <FileCode className="w-5 h-5 text-primary-600" />
                  <div>
                    <h3 className="font-medium text-gray-900">
                      {result.chunk.file_name}
                    </h3>
                    <p className="text-sm text-gray-500">
                      Lines {result.chunk.line_start}-{result.chunk.line_end} • {result.chunk.language}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-500">Relevance:</span>
                  <span className="bg-primary-100 text-primary-800 text-xs font-medium px-2.5 py-0.5 rounded">
                    {(result.score * 100).toFixed(1)}%
                  </span>
                </div>
              </div>

              {/* Code Preview */}
              <div className="overflow-x-auto">
                <SyntaxHighlighter
                  language={result.chunk.language}
                  style={vscDarkPlus as any}
                  customStyle={{
                    margin: 0,
                    borderRadius: '0.5rem',
                    fontSize: '0.875rem',
                  }}
                >
                  {result.chunk.content}
                </SyntaxHighlighter>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-400">
          <Search className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p className="text-lg">Search for code in your codebase</p>
          <p className="text-sm mt-2">
            Try searching for functionality like "login", "database", or "validation"
          </p>
        </div>
      )}
    </div>
  );
}
