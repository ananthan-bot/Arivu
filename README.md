# Arivu

**Enterprise-grade Retrieval-Augmented Generation platform** — built to demonstrate production RAG architecture, not a notebook demo.

> Status: actively in development. This README reflects what's actually built and tested, updated as each milestone ships — see Roadmap below for what's next.

---

## What's built so far

A working document ingestion pipeline, verified end-to-end against a real Postgres + pgvector instance:

    Upload (PDF/TXT/MD)
       -> Extraction (page-aware text extraction)
       -> Chunking (heading-aware + recursive, with token-budget overlap)
       -> Embedding (BGE-small, 384-dim)
       -> Storage (Postgres + pgvector)

Every stage is a separately-testable service behind a clean interface — swapping the embedding model, adding a new file format, or moving from pgvector to a dedicated vector DB later means changing one module, not the pipeline.

## Why these design choices

**Heading-aware + recursive chunking, not fixed-size.** Fixed-size chunking routinely slices a sentence or table row in half, which damages both embedding quality and citation accuracy. This implementation splits on document structure first, then recursively narrows to a token budget with overlap, so a claim spanning a chunk boundary is still retrievable.

**BGE-small over a larger model.** Runs locally on CPU with no API cost, and BGE's contrastive retrieval-specific training puts it near the top of MTEB retrieval benchmarks at this size. The model name is a config value, not hardcoded, so swapping to E5, NV-Embed, or an API-based embedder is a config change.

**pgvector instead of a dedicated vector DB (for now).** One fewer service to run and deploy while the project is this size. The repository layer is the seam — retrieval code talks to a ChunkRepository interface, not to SQL directly, so migrating to Qdrant later doesn't touch business logic.

**Clean Architecture / Domain-Driven layout.** Every module has its own controllers/services/repositories/schemas/models. Controllers depend on services, services depend on repository interfaces, never on ORM/DB code directly.

## Tech stack

| Layer | Choice |
|---|---|
| API | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL + pgvector |
| Embeddings | sentence-transformers (BGE-small-en-v1.5) |
| Chunking | Custom heading-aware recursive splitter |
| Testing | pytest (unit + integration) |
| CI | GitHub Actions (lint + test against a real Postgres service container) |
| Deployment | Docker / Docker Compose |

## Project structure

    backend/
      app/
        core/                 # config, database
        modules/
          ingestion/
            controllers/      # HTTP routes
            services/         # extraction, chunking, embedding, orchestration
            repositories/     # data access
            schemas/          # request/response models
            models/           # ORM models
          retrieval/          # hybrid search (in progress)
      tests/
        unit/
        integration/
    infrastructure/
      docker-compose.yml

## Running locally

    cd infrastructure
    docker compose up --build

Or without Docker:

    cd backend
    python -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    uvicorn app.main:app --reload

API docs available at http://localhost:8000/docs once running.

## Testing

    cd backend
    pytest tests/ -v

8 tests currently passing (unit tests for extraction/chunking, plus an integration test running the full pipeline against a live database).

## Roadmap

- [x] Document ingestion pipeline (extraction -> chunking -> embedding -> storage)
- [ ] Hybrid retrieval (vector + BM25 via reciprocal rank fusion)
- [ ] Cross-encoder reranking
- [ ] LLM answer generation with citations
- [ ] Hallucination guard (low-confidence retrieval -> decline to answer)
- [ ] Retrieval evaluation pipeline (precision/recall on a fixed test set)
- [ ] Frontend chat interface
- [ ] Deployment (Render/Railway + Vercel)

Deliberately out of scope for now: multi-agent orchestration, OCR, multi-tenant RBAC, admin dashboard, full observability stack.

## License

MIT
