import { useState, useEffect } from 'react';
import { Database, FileCode, Loader, TrendingUp } from 'lucide-react';
import { apiService } from '../services/api';
import type { Stats } from '../types';

export default function StatsPanel() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await apiService.getStats();
      setStats(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load stats');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12 text-red-600">
        <p className="text-lg font-medium">Failed to load statistics</p>
        <p className="text-sm mt-2">{error}</p>
        <button onClick={loadStats} className="btn-primary mt-4">
          Retry
        </button>
      </div>
    );
  }

  if (!stats) return null;

  const languages = Object.entries(stats.languages).sort((a, b) => b[1] - a[1]);
  const totalChunks = stats.total_chunks;

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Statistics</h2>
        <p className="text-gray-600">Overview of your codebase</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm font-medium">Total Chunks</p>
              <p className="text-3xl font-bold mt-2">{totalChunks}</p>
            </div>
            <Database className="w-12 h-12 opacity-50" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm font-medium">Files Indexed</p>
              <p className="text-3xl font-bold mt-2">{stats.files}</p>
            </div>
            <FileCode className="w-12 h-12 opacity-50" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm font-medium">Languages</p>
              <p className="text-3xl font-bold mt-2">{languages.length}</p>
            </div>
            <TrendingUp className="w-12 h-12 opacity-50" />
          </div>
        </div>
      </div>

      {/* Languages Breakdown */}
      {languages.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Languages Breakdown
          </h3>
          <div className="space-y-4">
            {languages.map(([language, count]) => {
              const percentage = (count / totalChunks) * 100;
              return (
                <div key={language}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700 capitalize">
                      {language}
                    </span>
                    <span className="text-sm text-gray-600">
                      {count} chunks ({percentage.toFixed(1)}%)
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Collection Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <Database className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-medium text-blue-900 mb-1">Vector Database</h3>
            <p className="text-sm text-blue-800">
              Collection: <span className="font-mono">{stats.collection_name}</span>
            </p>
            <p className="text-sm text-blue-700 mt-2">
              All code chunks are stored as embeddings in ChromaDB for fast semantic search.
            </p>
          </div>
        </div>
      </div>

      {/* Refresh Button */}
      <div className="text-center">
        <button onClick={loadStats} className="btn-secondary inline-flex items-center space-x-2">
          <Loader className="w-4 h-4" />
          <span>Refresh Stats</span>
        </button>
      </div>
    </div>
  );
}
