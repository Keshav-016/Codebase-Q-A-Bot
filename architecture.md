# Codebase Q&A Bot — Architecture

## Overview

A RAG (retrieval-augmented generation) system that ingests a GitHub repository, indexes it as searchable vector embeddings, and answers natural-language questions about the code with citations back to the source files.

## High-Level Flow

```
User pastes repo URL
        |
        v
React UI --> Django/DRF API --> GitHubIngest record created (status: pending)
        |
        v
Celery task picks up job (via Redis broker)
        |
        v
Pull files from GitHub API --> Chunk by function/class --> Embed chunks (sentence-transformers)
        |
        v
Store chunks + vectors in Postgres (pgvector) --> status: ready
        |
        v
User asks a question in the UI
        |
        v
Django/DRF API --> embed question --> similarity search (pgvector) --> top-k chunks
        |
        v
Chunks + question --> LLM --> generated answer
        |
        v
Response returned with answer + source file/line citations --> rendered in React UI
```

## Components

### 1. Django + DRF (API layer)
- Exposes endpoints for: starting ingestion, polling ingestion status, asking questions
- Owns the `GitHubIngest` and `CodeChunk` models
- Thin controller layer — heavy lifting (chunking, embedding, retrieval) lives in service modules, not views, to keep it testable

### 2. Celery + Redis (async ingestion)
- Ingestion is slow (network calls + embedding), so it never runs in the request/response cycle
- Redis is the broker; Celery worker processes ingestion jobs
- API polls/reports job status (`pending` → `processing` → `ready` / `failed`)

### 3. Chunking service
- Python files: parsed with `ast`, chunked at function/class boundaries so each chunk is semantically complete
- Other languages: simpler line-window or regex-based splitting (upgrade path: tree-sitter for proper AST parsing across languages)
- Each chunk stores: file path, start/end line, chunk text, repo reference

### 4. Embedding + vector store
- sentence-transformers model generates embeddings for each chunk (and later, each question)
- Postgres + pgvector stores chunk text + vector + metadata
- Similarity search via pgvector's cosine distance operator, top-k retrieval

### 5. Retrieval + generation
- Question embedded with the same model used for chunks (consistency matters here)
- Top-k chunks retrieved, optionally re-ranked (score threshold or cross-encoder)
- Chunks + question assembled into a prompt, sent to the LLM
- LLM response returned alongside the source chunks used, so the UI can show citations

### 6. React frontend
- Two views: ingestion (paste URL, see status) and chat (ask questions, see answers + citations)
- Polls the ingestion status endpoint until `ready`
- Renders each answer with a collapsible "sources" section listing file paths and line ranges

## Data Models (simplified)

```
GitHubIngest
- id
- repo_url
- status (pending | processing | ready | failed)
- created_at
- last_synced_at

CodeChunk
- id
- ingest (FK -> GitHubIngest)
- file_path
- start_line
- end_line
- content
- embedding (vector)
```

## Deployment

- Local dev: Docker Compose spins up Django, Postgres (with pgvector extension), Redis, and a Celery worker
- Production: same containers deployed to Railway or an EC2 instance, reusing the existing CI/CD pipeline
- Environment variables for GitHub token, LLM API key, DB connection

## Key Design Decisions

- **Function/class-level chunking over fixed-size chunking** — preserves semantic boundaries so retrieved chunks are coherent, not arbitrary mid-function cuts
- **Async ingestion via Celery** — keeps the API responsive; ingestion of a large repo shouldn't time out a request
- **Same embedding model for chunks and questions** — mismatched embedding spaces silently degrade retrieval quality
- **Citations returned with every answer** — makes the system auditable and is the detail that distinguishes it from a generic chatbot wrapper
