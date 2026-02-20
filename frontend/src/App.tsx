import { useState, useEffect } from 'react';
import { Upload, MessageSquare, Search, Database, Github } from 'lucide-react';
import ChatInterface from './components/ChatInterface';
import FileUploader from './components/FileUploader';
import SearchPanel from './components/SearchPanel';
import StatsPanel from './components/StatsPanel';
import { apiService } from './services/api';
import type { HealthResponse } from './types';

type Tab = 'chat' | 'upload' | 'search' | 'stats';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('upload');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const data = await apiService.getHealth();
      setHealth(data);
      setIsConnected(data.status === 'healthy');
    } catch (error) {
      setIsConnected(false);
      console.error('Backend not connected:', error);
    }
  };

  const tabs = [
    { id: 'upload' as Tab, label: 'Upload Code', icon: Upload },
    { id: 'chat' as Tab, label: 'Chat', icon: MessageSquare },
    { id: 'search' as Tab, label: 'Search', icon: Search },
    { id: 'stats' as Tab, label: 'Stats', icon: Database },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-2 rounded-lg">
                <MessageSquare className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">CodeMate AI</h1>
                <p className="text-sm text-gray-500">RAG-Powered Code Assistant</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div
                  className={`w-3 h-3 rounded-full ${
                    isConnected ? 'bg-green-500' : 'bg-red-500'
                  } animate-pulse`}
                />
                <span className="text-sm text-gray-600">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              {health && (
                <div className="text-sm text-gray-600">
                  <span className="font-medium">{health.total_chunks}</span> chunks
                </div>
              )}
              <a
                href="https://github.com/SaharHalili95/codemate-ai"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                <Github className="w-6 h-6" />
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!isConnected && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center space-x-2 text-red-800">
              <div className="w-2 h-2 bg-red-500 rounded-full" />
              <p className="font-medium">Backend is not connected</p>
            </div>
            <p className="text-sm text-red-600 mt-1">
              Make sure the FastAPI backend is running on http://localhost:8000
            </p>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-md mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-1 p-2" aria-label="Tabs">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`
                      flex items-center space-x-2 px-4 py-2 rounded-lg font-medium text-sm transition-all
                      ${
                        activeTab === tab.id
                          ? 'bg-primary-600 text-white shadow-md'
                          : 'text-gray-600 hover:bg-gray-100'
                      }
                    `}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'upload' && <FileUploader onUploadSuccess={checkHealth} />}
            {activeTab === 'chat' && <ChatInterface />}
            {activeTab === 'search' && <SearchPanel />}
            {activeTab === 'stats' && <StatsPanel />}
          </div>
        </div>

        {/* Footer */}
        <footer className="text-center text-sm text-gray-600 mt-8">
          <p>
            Built with ❤️ by{' '}
            <a
              href="https://github.com/SaharHalili95"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              Sahar Halili
            </a>
          </p>
          <p className="mt-1">
            Powered by OpenAI • ChromaDB • FastAPI • React
          </p>
        </footer>
      </main>
    </div>
  );
}

export default App;
