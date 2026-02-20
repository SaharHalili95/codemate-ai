# 🤖 CodeMate AI - RAG-Powered Code Assistant

![CI](https://github.com/SaharHalili95/codemate-ai/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

🌐 **[Live Demo](https://codemate-ai.vercel.app)** (Coming Soon)

A professional RAG-powered code assistant that lets you chat with your codebase using AI. Upload your code, ask questions in natural language, and get intelligent answers with relevant code snippets.

![CodeMate AI Demo](docs/demo.gif)

## ✨ Features

- 🤖 **AI-Powered Q&A** - Ask questions about your code in natural language
- 🔍 **Semantic Search** - Find code by meaning, not just keywords
- 📁 **Multiple Languages** - Python, JavaScript, TypeScript, Java, C++, Go, Rust
- 💬 **Chat Interface** - Interactive conversation with code context
- 🎨 **Syntax Highlighting** - Beautiful code display with Prism
- ⚡ **Fast Retrieval** - ChromaDB vector database for lightning-quick searches
- 🚀 **Modern Stack** - React 18, TypeScript, FastAPI, Tailwind CSS
- 📊 **Analytics Dashboard** - View statistics about your indexed codebase

## 🏗️ Architecture

### RAG Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                     RAG Architecture                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User Question                                               │
│       │                                                      │
│       ▼                                                      │
│  Embedding Service (OpenAI)                                  │
│       │                                                      │
│       ▼                                                      │
│  Vector Search (ChromaDB)                                    │
│       │                                                      │
│       ▼                                                      │
│  Top K Relevant Code Chunks                                  │
│       │                                                      │
│       ▼                                                      │
│  LLM with Context (GPT-4/Claude)                             │
│       │                                                      │
│       ▼                                                      │
│  AI-Generated Answer                                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Tech Stack

**Backend:**
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [OpenAI API](https://openai.com/) - Embeddings & LLM
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [Uvicorn](https://www.uvicorn.org/) - ASGI server

**Frontend:**
- [React 18](https://react.dev/) + TypeScript
- [Vite](https://vitejs.dev/) - Build tool
- [Tailwind CSS](https://tailwindcss.com/) - Styling
- [Prism](https://prismjs.com/) - Syntax highlighting
- [React Markdown](https://github.com/remarkjs/react-markdown) - Markdown rendering

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the server
python -m app.main
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env
# Default API URL is http://localhost:8000

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 📖 Usage

### 1. Upload Code

- Click on the "Upload Code" tab
- Drag & drop a code file or click to browse
- Supported formats: `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.go`, `.rs`
- The system will parse, chunk, and index your code

### 2. Chat with Your Code

- Switch to the "Chat" tab
- Ask questions like:
  - "How does the login function work?"
  - "Explain the authentication flow"
  - "What does this error handling code do?"
- Get AI-powered answers with relevant code snippets

### 3. Semantic Search

- Use the "Search" tab for direct code search
- Search by functionality, not just keywords
- View relevance scores for each result

### 4. View Statistics

- Check the "Stats" tab to see:
  - Total chunks indexed
  - Number of files
  - Language breakdown
  - Database information

## 🎯 API Endpoints

### Backend API

```
POST /upload          - Upload a code file
POST /chat            - Chat with your codebase
POST /chat/stream     - Stream chat responses
POST /search          - Semantic code search
DELETE /files/{name}  - Delete a file's chunks
GET /stats            - Get database statistics
GET /                 - Health check
```

Full API documentation available at `http://localhost:8000/docs` (Swagger UI)

## 🛠️ Development

### Project Structure

```
codemate-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── core/
│   │   │   └── config.py        # Configuration
│   │   ├── models/
│   │   │   └── schemas.py       # Data models
│   │   └── services/
│   │       ├── embeddings.py    # Embedding generation
│   │       ├── vector_store.py  # Vector DB management
│   │       ├── parser.py        # Code parsing & chunking
│   │       └── llm.py           # LLM integration
│   ├── requirements.txt
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── services/          # API integration
│   │   ├── types/             # TypeScript types
│   │   └── App.tsx            # Main app
│   └── package.json
└── README.md
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests (if available)
cd frontend
npm test
```

## 🚀 Deployment

### Deploy Backend (Railway/Render)

1. Push your code to GitHub
2. Connect your repository to [Railway](https://railway.app/) or [Render](https://render.com/)
3. Set environment variables:
   - `OPENAI_API_KEY`
   - `LLM_PROVIDER=openai`
   - Other settings from `.env.example`
4. Deploy!

### Deploy Frontend (Vercel)

```bash
cd frontend
npm run build

# Deploy to Vercel
vercel --prod
```

Or connect your GitHub repository to [Vercel](https://vercel.com/) for automatic deployments.

## 🔧 Configuration

### Environment Variables

**Backend** (`.env`):
```bash
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K=5
MODEL_NAME=gpt-4-turbo-preview
```

**Frontend** (`.env`):
```bash
VITE_API_URL=http://localhost:8000
```

## 📊 Key Concepts

### Embeddings
Vector representations of text that capture semantic meaning. Similar code produces similar embeddings.

### Vector Database
Specialized database for storing and searching embeddings efficiently using similarity metrics.

### RAG (Retrieval Augmented Generation)
An architecture that combines information retrieval with LLM generation for accurate, context-aware responses.

### Chunking
Splitting code into smaller, meaningful segments for better embedding quality and retrieval.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for the Embeddings API and GPT models
- ChromaDB for the vector database
- FastAPI for the excellent Python web framework
- React team for the amazing UI library

## 📬 Contact

**Sahar Halili**
- GitHub: [@SaharHalili95](https://github.com/SaharHalili95)
- LinkedIn: [Sahar Halili](https://www.linkedin.com/in/sahar-halili-36ba38300)
- Email: sahar_halili@icloud.com

## 🌟 Star History

If you find this project useful, please consider giving it a star ⭐

---

<div align="center">
Built with ❤️ by Sahar Halili
</div>
