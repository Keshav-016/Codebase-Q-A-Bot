# Codebase Q&A Bot — Planning

RAG system over GitHub repos. Paste a repo URL, ask questions, get answers with source-file citations. Built to demonstrate real retrieval-augmented generation (not a thin LLM wrapper) plus backend depth via Django.

## Goal

Ship a working, deployed demo with a public link, good enough to walk an interviewer through end-to-end: ingestion → chunking → embedding → retrieval → generation → citation.

## Tech Stack

- **Backend:** Django + Django REST Framework
- **Async jobs:** Celery + Redis (repo ingestion runs in background)
- **DB:** PostgreSQL + pgvector (chunk storage + similarity search)
- **Embeddings:** sentence-transformers (open-source, no API cost)
- **LLM:** any hosted API (OpenAI/Anthropic) for the final answer generation step
- **Frontend:** React (chat UI)
- **Infra:** Docker Compose locally, deploy to Railway or EC2

## Milestones

### Phase 1 — Backend skeleton (Days 1–2)
- Django + DRF project scaffolded
- `GitHubIngest` model (repo url, status, last_synced)
- Postgres + pgvector running in Docker
- Basic health-check endpoint

### Phase 2 — Ingestion pipeline (Days 3–5)
- Pull repo files via GitHub API (PyGithub)
- Chunk by function/class using `ast` for Python files; simpler splitting for other languages
- Embed chunks with sentence-transformers, store in pgvector
- Wire ingestion into Celery so it runs async, with a status endpoint to poll

### Phase 3 — Retrieval + answer endpoint (Days 6–8)
- DRF endpoint: question in → embed → similarity search top-k chunks → pass to LLM → answer out
- Return source file paths + line ranges alongside the answer
- Add a re-ranking or score-threshold step to improve retrieval quality

### Phase 4 — Frontend (Days 9–11)
- React chat UI: paste repo URL, show ingestion progress, ask questions
- Render answers with citations (filename + line range) under each response

### Phase 5 — Deploy + polish (Days 12–14)
- Docker Compose: Django + Postgres + Redis + Celery worker
- Deploy to Railway or EC2 (reuse existing CI/CD pipeline)
- Write README with architecture diagram and a short demo GIF
- Add the live link + one-line bullet to resume

## Success Criteria

- Can ingest a real repo (e.g. one of my own) end-to-end without manual intervention
- Answers are grounded — citations point to the actual relevant file/lines, not hallucinated
- Ingestion doesn't block the API (verified via Celery async flow)
- Deployed and reachable via a public URL

## Stretch Goals (only if time allows)

- Cross-encoder re-ranking instead of raw cosine similarity
- Multi-repo support (switch between ingested repos in the UI)
- Streaming answer responses (SSE) instead of waiting for full completion

## Risks / Open Questions

- Chunking quality for non-Python languages — may need tree-sitter if regex splitting is too crude
- Large repos may take a long time to embed — may need to cap file count or size for the demo
- LLM API cost if demoing publicly — consider rate-limiting the endpoint
