import { useState } from 'react';
import { Search, FileCode } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { clientStorage, type CodeChunk } from '../services/clientStorage';

export default function SearchPanel() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<CodeChunk[]>([]);
  const [searched, setSearched] = useState(false);

  const handleSearch = () => {
    if (!query.trim()) return;

    setSearched(true);
    const searchResults = clientStorage.search(query, 5);
    setResults(searchResults);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Code Search</h2>
        <p className="text-gray-600">
          Search for code snippets by keywords
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
            placeholder="e.g., 'function', 'class', 'import'..."
            className="w-full pl-10 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
        <button
          onClick={handleSearch}
          disabled={!query.trim()}
          className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Search
        </button>
      </div>

      {/* Results */}
      {searched && results.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <FileCode className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p className="text-lg font-medium">No results found</p>
          <p className="text-sm mt-2">Try a different query or upload more code</p>
        </div>
      ) : results.length > 0 ? (
        <div className="space-y-4">
          {results.map((result) => (
            <div key={result.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <FileCode className="w-4 h-4 text-gray-500" />
                    <span className="font-medium text-gray-900">{result.fileName}</span>
                  </div>
                  <span className="text-sm text-gray-500">
                    Lines {result.lineStart}-{result.lineEnd}
                  </span>
                </div>
              </div>
              <div className="p-4">
                <SyntaxHighlighter
                  language={result.language}
                  style={vscDarkPlus}
                  customStyle={{ margin: 0, borderRadius: '0.5rem' }}
                >
                  {result.content}
                </SyntaxHighlighter>
              </div>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
