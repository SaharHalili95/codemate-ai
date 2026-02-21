import { Database, FileCode, Trash2 } from 'lucide-react';
import { clientStorage } from '../services/clientStorage';

interface StatsPanelProps {
  stats: {
    totalFiles: number;
    totalChunks: number;
    languages: Record<string, number>;
  };
}

export default function StatsPanel({ stats }: StatsPanelProps) {
  const languages = Object.entries(stats.languages).sort((a, b) => b[1] - a[1]);
  const files = clientStorage.getFiles();

  const handleClearAll = () => {
    if (confirm('Are you sure you want to delete all uploaded files?')) {
      clientStorage.clear();
      window.location.reload();
    }
  };

  const handleDeleteFile = (fileName: string) => {
    if (confirm(`Delete ${fileName}?`)) {
      clientStorage.deleteFile(fileName);
      window.location.reload();
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Statistics</h2>
        <p className="text-gray-600">Overview of your uploaded code</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm font-medium">Total Chunks</p>
              <p className="text-3xl font-bold mt-2">{stats.totalChunks}</p>
            </div>
            <Database className="w-12 h-12 opacity-50" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm font-medium">Files Uploaded</p>
              <p className="text-3xl font-bold mt-2">{stats.totalFiles}</p>
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
            <FileCode className="w-12 h-12 opacity-50" />
          </div>
        </div>
      </div>

      {/* Language Breakdown */}
      {languages.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Languages</h3>
          <div className="space-y-3">
            {languages.map(([lang, count]) => (
              <div key={lang}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700 capitalize">{lang}</span>
                  <span className="text-sm text-gray-500">{count} files</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full transition-all"
                    style={{ width: `${(count / stats.totalFiles) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Files List */}
      {files.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Uploaded Files</h3>
            <button
              onClick={handleClearAll}
              className="flex items-center space-x-2 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              <span>Clear All</span>
            </button>
          </div>
          <div className="space-y-2">
            {files.map((file) => (
              <div
                key={file.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <FileCode className="w-5 h-5 text-gray-500" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">{file.fileName}</p>
                    <p className="text-xs text-gray-500 capitalize">{file.language}</p>
                  </div>
                </div>
                <button
                  onClick={() => handleDeleteFile(file.fileName)}
                  className="text-red-600 hover:text-red-700 p-1"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
