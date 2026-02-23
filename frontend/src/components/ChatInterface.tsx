import { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Bot, User, AlertCircle, Plus, History, Trash2, ChevronDown } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { openaiService } from '../services/openai';
import { clientStorage, ChatSession } from '../services/clientStorage';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatInterfaceProps {
  apiKey: string;
}

export default function ChatInterface({ apiKey }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const historyRef = useRef<HTMLDivElement>(null);

  // Load sessions list on mount
  useEffect(() => {
    setSessions(clientStorage.getChatSessions());
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Close history dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (historyRef.current && !historyRef.current.contains(e.target as Node)) {
        setShowHistory(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Persist the current session to localStorage
  const persistSession = useCallback((sessionId: string, msgs: Message[]) => {
    const existing = clientStorage.getChatSession(sessionId);
    if (existing) {
      existing.messages = msgs;
      existing.updatedAt = Date.now();
      clientStorage.saveChatSession(existing);
    }
    setSessions(clientStorage.getChatSessions());
  }, []);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    if (!apiKey) {
      alert('Please set your OpenAI API key first!');
      return;
    }

    const userMessage: Message = {
      role: 'user',
      content: input,
    };

    // If no active session, create one with auto-generated name
    let sessionId = currentSessionId;
    if (!sessionId) {
      const newSession: ChatSession = {
        id: Date.now().toString(),
        name: clientStorage.generateSessionName(input),
        messages: [],
        createdAt: Date.now(),
        updatedAt: Date.now(),
      };
      clientStorage.saveChatSession(newSession);
      sessionId = newSession.id;
      setCurrentSessionId(sessionId);
    }

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput('');
    setLoading(true);

    // Persist after user message
    persistSession(sessionId, updatedMessages);

    try {
      // Search for relevant code chunks
      const context = clientStorage.search(input, 5);

      // Get AI response with context
      const response = await openaiService.chat(
        apiKey,
        input,
        context,
        messages
      );

      const assistantMessage: Message = {
        role: 'assistant',
        content: response,
      };

      const finalMessages = [...updatedMessages, assistantMessage];
      setMessages(finalMessages);

      // Persist after assistant response
      persistSession(sessionId, finalMessages);
    } catch (error: any) {
      const errorMessage: Message = {
        role: 'assistant',
        content: `Error: ${error.message || 'Failed to get response'}`,
      };
      const finalMessages = [...updatedMessages, errorMessage];
      setMessages(finalMessages);
      persistSession(sessionId, finalMessages);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Start a brand-new chat session
  const handleNewChat = () => {
    setMessages([]);
    setCurrentSessionId(null);
    setShowHistory(false);
  };

  // Load a previous session
  const handleLoadSession = (session: ChatSession) => {
    setMessages(session.messages);
    setCurrentSessionId(session.id);
    setShowHistory(false);
  };

  // Delete a session
  const handleDeleteSession = (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    clientStorage.deleteChatSession(sessionId);
    setSessions(clientStorage.getChatSessions());
    // If the deleted session is currently active, reset
    if (currentSessionId === sessionId) {
      setMessages([]);
      setCurrentSessionId(null);
    }
  };

  const stats = clientStorage.getStats();

  return (
    <div className="flex flex-col h-[600px]">
      {/* Header with Chat History Controls */}
      <div className="flex items-center justify-between mb-4">
        <div className="text-left">
          <h2 className="text-2xl font-bold text-gray-900">Chat with Your Code</h2>
          <p className="text-sm text-gray-600">
            {currentSessionId
              ? sessions.find(s => s.id === currentSessionId)?.name || 'Current Session'
              : 'New Conversation'}
          </p>
        </div>

        <div className="flex items-center space-x-2">
          {/* New Chat Button */}
          <button
            onClick={handleNewChat}
            className="flex items-center space-x-1 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            title="New Chat"
          >
            <Plus className="w-4 h-4" />
            <span>New Chat</span>
          </button>

          {/* History Dropdown */}
          <div className="relative" ref={historyRef}>
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="flex items-center space-x-1 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              title="Chat History"
            >
              <History className="w-4 h-4" />
              <span>History</span>
              {sessions.length > 0 && (
                <span className="ml-1 bg-primary-600 text-white text-xs rounded-full px-1.5 py-0.5 leading-none">
                  {sessions.length}
                </span>
              )}
              <ChevronDown className={`w-3 h-3 transition-transform ${showHistory ? 'rotate-180' : ''}`} />
            </button>

            {showHistory && (
              <div className="absolute right-0 top-full mt-1 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-72 overflow-y-auto">
                {sessions.length === 0 ? (
                  <div className="p-4 text-sm text-gray-500 text-center">
                    No saved sessions yet. Start chatting to create one.
                  </div>
                ) : (
                  sessions.map((session) => (
                    <div
                      key={session.id}
                      onClick={() => handleLoadSession(session)}
                      className={`flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-gray-50 border-b border-gray-100 last:border-b-0 ${
                        currentSessionId === session.id ? 'bg-primary-50' : ''
                      }`}
                    >
                      <div className="flex-1 min-w-0 mr-2">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {session.name}
                        </p>
                        <p className="text-xs text-gray-500">
                          {session.messages.length} messages &middot;{' '}
                          {new Date(session.updatedAt).toLocaleDateString(undefined, {
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </p>
                      </div>
                      <button
                        onClick={(e) => handleDeleteSession(e, session.id)}
                        className="flex-shrink-0 p-1 text-gray-400 hover:text-red-500 rounded transition-colors"
                        title="Delete session"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {stats.totalFiles === 0 && (
        <div className="mb-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm text-yellow-800">
                No code files uploaded yet. Please upload some code files first!
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto bg-gray-50 rounded-lg p-4 space-y-4 mb-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <Bot className="w-16 h-16 mb-4" />
            <p className="text-lg">Start a conversation!</p>
            <p className="text-sm mt-2">Try asking:</p>
            <ul className="text-sm mt-2 space-y-1 text-center">
              <li>"What does this code do?"</li>
              <li>"Explain the main function"</li>
              <li>"How can I improve this code?"</li>
            </ul>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex items-start space-x-3 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                )}

                <div
                  className={`max-w-[80%] rounded-lg p-4 ${
                    message.role === 'user'
                      ? 'bg-primary-600 text-white'
                      : 'bg-white text-gray-900 shadow-sm'
                  }`}
                >
                  {message.role === 'user' ? (
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  ) : (
                    <div className="prose prose-sm max-w-none">
                      <ReactMarkdown
                        components={{
                          code({ inline, className, children, ...props }: any) {
                            const match = /language-(\w+)/.exec(className || '');
                            return !inline && match ? (
                              <SyntaxHighlighter
                                style={vscDarkPlus}
                                language={match[1]}
                                PreTag="div"
                                {...props}
                              >
                                {String(children).replace(/\n$/, '')}
                              </SyntaxHighlighter>
                            ) : (
                              <code className={className} {...props}>
                                {children}
                              </code>
                            );
                          },
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  )}
                </div>

                {message.role === 'user' && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center">
                    <User className="w-5 h-5 text-white" />
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <div className="bg-white rounded-lg p-4 shadow-sm">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="flex space-x-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question about your code..."
          disabled={loading || !apiKey}
          className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50"
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim() || !apiKey}
          className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 transition-colors"
        >
          <Send className="w-5 h-5" />
          <span>Send</span>
        </button>
      </div>
    </div>
  );
}
