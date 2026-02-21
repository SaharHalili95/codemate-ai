# 🤖 CodeMate AI - Client-Side Code Assistant

![CI](https://github.com/SaharHalili95/codemate-ai/actions/workflows/ci.yml/badge.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

🌐 **[Live Demo](https://saharhalili95.github.io/codemate-ai/)**

A lightweight, privacy-first code assistant that runs entirely in your browser. Upload code files, search through them, and chat with AI about your code - all without sending your code to any server!

## ✨ Features

- 🔒 **100% Client-Side** - Your code never leaves your browser
- 🤖 **AI-Powered Chat** - Ask questions about your code using OpenAI's GPT-4
- 🔍 **Code Search** - Find code snippets by keywords
- 📁 **Multiple Languages** - Python, JavaScript, TypeScript, Java, C++, Go, Rust
- 💬 **Interactive Chat** - Conversational interface with code context
- 🎨 **Syntax Highlighting** - Beautiful code display
- 📊 **Statistics** - View analytics about your uploaded files
- 🔑 **API Key Management** - Securely stored in your browser's localStorage

## 🚀 Quick Start

### Live Demo

Visit **[https://saharhalili95.github.io/codemate-ai/](https://saharhalili95.github.io/codemate-ai/)**

1. **Get an OpenAI API Key**
   - Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - Create a new API key
   - Copy it

2. **Set Your API Key**
   - Click "Set API Key" in the top right
   - Paste your key
   - Click "Save" (it's stored securely in your browser)

3. **Upload Code**
   - Drag and drop a code file (.py, .js, .ts, etc.)
   - Or click to browse and select

4. **Start Chatting**
   - Go to the "Chat" tab
   - Ask questions about your code!

### Local Development

```bash
# Clone the repository
git clone https://github.com/SaharHalili95/codemate-ai.git
cd codemate-ai/frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:5173
```

## 🏗️ How It Works

### Client-Side Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Client-Side Processing                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Upload Code → localStorage                           │
│  2. Parse & Chunk Code                                   │
│  3. User Question                                        │
│  4. Search Relevant Chunks (keyword matching)            │
│  5. Send Context + Question → OpenAI API                 │
│  6. Display AI Response                                  │
│                                                          │
│  All processing happens in your browser!                 │
│  Code never sent anywhere except OpenAI for chat.        │
└─────────────────────────────────────────────────────────┘
```

## 💻 Tech Stack

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Markdown** - Markdown rendering
- **React Syntax Highlighter** - Code highlighting

### AI Integration
- **OpenAI API** - GPT-4 for intelligent responses
- **localStorage** - Client-side storage

### Services
- **clientStorage.ts** - Manages code files in localStorage
- **openai.ts** - Direct OpenAI API integration

## 📦 Project Structure

```
codemate-ai/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── App.tsx           # Main app component
│   │   │   ├── ChatInterface.tsx # Chat UI
│   │   │   ├── FileUploader.tsx  # File upload
│   │   │   ├── SearchPanel.tsx   # Code search
│   │   │   └── StatsPanel.tsx    # Statistics
│   │   ├── services/
│   │   │   ├── clientStorage.ts  # localStorage management
│   │   │   └── openai.ts         # OpenAI API calls
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 🔑 API Key Security

- Your OpenAI API key is stored in your browser's localStorage
- It's never sent to any server except OpenAI's official API
- You can clear it anytime from your browser settings
- Consider setting usage limits on your OpenAI account

## 🌟 Features in Detail

### 1. File Upload
- Drag & drop or browse to select files
- Supports .py, .js, .ts, .tsx, .jsx, .java, .cpp, .go, .rs
- Files stored locally in your browser
- Automatic language detection

### 2. Code Search
- Simple keyword-based search
- Searches through all uploaded files
- Displays matches with syntax highlighting
- Shows file name and line numbers

### 3. AI Chat
- Ask questions about your uploaded code
- AI retrieves relevant code chunks as context
- Supports conversation history
- Markdown formatting in responses
- Syntax-highlighted code blocks

### 4. Statistics
- Total files and chunks
- Language breakdown
- File management (delete individual files or clear all)

## 🚀 Deployment

The app is automatically deployed to GitHub Pages when changes are pushed to main.

To deploy manually:

```bash
cd frontend
npm run build
npm run deploy
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

## 👤 Author

**Sahar Halili**

- GitHub: [@SaharHalili95](https://github.com/SaharHalili95)
- Portfolio: [saharhalili95.github.io/html-portfolio](https://saharhalili95.github.io/html-portfolio/)
- LinkedIn: [Sahar Halili](https://www.linkedin.com/in/sahar-halili-36ba38300)

## 🙏 Acknowledgments

- OpenAI for the GPT API
- React and Vite communities
- All open-source contributors

---

**Built with ❤️ and 🤖 AI**

⭐ Star this repo if you find it useful!
