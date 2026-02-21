import { useState } from 'react';
import { Upload, MessageSquare, Search, Database, Github, Key } from 'lucide-react';
import ChatInterface from './components/ChatInterface';
import FileUploader from './components/FileUploader';
import SearchPanel from './components/SearchPanel';
import StatsPanel from './components/StatsPanel';
import { clientStorage } from './services/clientStorage';

type Tab = 'upload' | 'chat' | 'search' | 'stats';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('upload');
  const [apiKey, setApiKey] = useState(localStorage.getItem('openai-api-key') || '');
  const [showApiKeyInput, setShowApiKeyInput] = useState(!apiKey);
  const [stats, setStats] = useState(clientStorage.getStats());

  const handleApiKeySave = () => {
    localStorage.setItem('openai-api-key', apiKey);
    setShowApiKeyInput(false);
  };

  const handleUploadSuccess = () => {
    setStats(clientStorage.getStats());
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
                <p className="text-sm text-gray-500">Client-Side Code Assistant</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowApiKeyInput(!showApiKeyInput)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  apiKey
                    ? 'bg-green-50 text-green-700 hover:bg-green-100'
                    : 'bg-yellow-50 text-yellow-700 hover:bg-yellow-100'
                }`}
              >
                <Key className="w-4 h-4" />
                <span>{apiKey ? 'API Key Set' : 'Set API Key'}</span>
              </button>
              <div className="text-sm text-gray-600">
                <span className="font-medium">{stats.totalChunks}</span> chunks
              </div>
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
        {/* API Key Setup */}
        {showApiKeyInput && (
          <div className="mb-6 bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">OpenAI API Key Setup</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Enter your OpenAI API Key
                </label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="sk-..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <p className="mt-2 text-sm text-gray-500">
                  Get your API key from{' '}
                  <a
                    href="https://platform.openai.com/api-keys"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:text-primary-700 font-medium"
                  >
                    platform.openai.com/api-keys
                  </a>
                </p>
                <p className="mt-1 text-sm text-gray-500">
                  Your API key is stored locally in your browser and never sent to any server except OpenAI.
                </p>
              </div>
              <button
                onClick={handleApiKeySave}
                disabled={!apiKey}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Save API Key
              </button>
            </div>
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
            {activeTab === 'upload' && <FileUploader onUploadSuccess={handleUploadSuccess} />}
            {activeTab === 'chat' && <ChatInterface apiKey={apiKey} />}
            {activeTab === 'search' && <SearchPanel />}
            {activeTab === 'stats' && <StatsPanel stats={stats} />}
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
            Powered by OpenAI • React • TypeScript • Client-Side Processing
          </p>
        </footer>
      </main>
    </div>
  );
}

export default App;
