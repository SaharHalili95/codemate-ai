# CodeMate AI - RAG-Powered Code Assistant

![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A full-stack AI code assistant built on **RAG (Retrieval Augmented Generation)** architecture. Upload code files, and ask natural-language questions about your codebase — the system retrieves the most relevant chunks using vector search and generates precise answers.

**Landing page:** https://saharhalili95.github.io/codemate-ai/ (the app itself runs locally; see below)

## Architecture

```
┌──────────────┐     upload      ┌─────────────────────────────────┐
│   Frontend   │ ─────────────▶  │          FastAPI Backend         │
│  React + TS  │                 │                                  │
│              │ ◀────────────── │  1. Parse code into chunks       │
│  Vite build  │   AI response   │  2. Generate embeddings (OpenAI) │
└──────────────┘                 │  3. Store in ChromaDB            │
                                 │  4. Semantic search on query     │
                                 │  5. LLM generates response       │
                                 └─────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| Backend | FastAPI (async), Python 3.11 |
| Vector DB | ChromaDB |
| Embeddings | OpenAI `text-embedding-3-small` |
| LLM | OpenAI or Anthropic (configurable) |
| Tests | pytest (API in demo mode, prompt building) |
| Infra | Docker, deploy configs for Render (backend) and Vercel (frontend) |

## Features

- End-to-end RAG pipeline: parsing → chunking → embeddings → vector search → generation
- One prompt builder for every LLM provider: OpenAI and Anthropic only differ in how the API is called
- Streaming chat responses (token by token)
- Semantic code search across entire codebases
- Supports Python, JavaScript, TypeScript, Java, C++, Go, Rust
- **Demo mode** — runs without an OpenAI API key for portfolio/demo purposes

## Local Development

### Backend

```bash
cd backend
pip install -r requirements.txt

# With OpenAI API key
OPENAI_API_KEY=sk-... uvicorn app.main:app --reload

# Without API key (demo mode)
DEMO_MODE=true uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
VITE_API_URL=http://localhost:8000 npm run dev
```

### Docker (full stack)

```bash
cp .env.example .env   # add OPENAI_API_KEY or set DEMO_MODE=true
docker-compose up
```

## Backend Structure

```
backend/app/
├── main.py            # App setup: lifespan, CORS, router registration
├── dependencies.py    # FastAPI dependencies
├── routes/            # HTTP layer only; __init__.py combines the routers
│   ├── health.py      # GET /, GET /stats
│   ├── files.py       # POST /upload, DELETE /files/{name}
│   ├── chat.py        # POST /chat, POST /chat/stream
│   └── search.py      # POST /search
├── services/
│   ├── codebase.py    # RAG pipeline: index, search, answer
│   ├── llm.py         # ChatModel interface: OpenAI, Anthropic, Demo
│   ├── embeddings.py  # Embedder interface: OpenAI, Demo
│   ├── vector_store.py
│   ├── parser.py      # Chunking by function or fixed size
│   └── demo.py        # Canned answers for demo mode
├── models/schemas.py
└── core/config.py
```

Demo mode swaps in `DemoEmbedder` and `DemoChatModel`, so routes and the RAG pipeline have no demo-specific branches.

## Tests

```bash
cd backend
pip install -r requirements.txt
pytest
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (needed for embeddings with either provider) | - |
| `DEMO_MODE` | Run without API key | `false` |
| `LLM_PROVIDER` | `openai` or `anthropic` | `openai` |
| `MODEL_NAME` | LLM model name | `gpt-4-turbo-preview` |
| `CHUNK_SIZE` | Tokens per chunk | `1000` |
| `TOP_K` | Chunks retrieved per query | `5` |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| POST | `/upload` | Upload and index a code file |
| POST | `/chat` | Ask a question about the codebase |
| POST | `/chat/stream` | Streaming chat |
| POST | `/search` | Semantic code search |
| DELETE | `/files/{name}` | Remove a file from the index |
| GET | `/stats` | Vector DB statistics |

## Author

**Sahar Halili**
- GitHub: [@SaharHalili95](https://github.com/SaharHalili95)
- LinkedIn: [Sahar Halili](https://www.linkedin.com/in/sahar-halili)
