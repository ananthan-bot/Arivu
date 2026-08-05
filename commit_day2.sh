#!/bin/bash
set -e

git add infrastructure/docker-compose.yml
git commit -m "fix: change postgres host port to 55432 to avoid conflicts"

git add backend/Dockerfile
git commit -m "fix: revert to standard pip install for requirements"

git add backend/app/main.py
git commit -m "fix: add startup hook to create pgvector extension and tables on boot"

git add backend/app/modules/retrieval/repositories/chunk_repository.py
git commit -m "feat: add chunk repository with vector search and BM25 data access"

git add backend/app/modules/retrieval/services/hybrid_retrieval.py
git commit -m "feat: add hybrid retrieval service using RRF fusion of vector and BM25"

git add backend/app/modules/retrieval/services/reranking.py
git commit -m "feat: add cross-encoder reranking service (top-50 to top-5)"

git add backend/app/modules/retrieval/services/context_builder.py
git commit -m "feat: add context builder with dedup, token budget and citation markers"

git add backend/app/modules/retrieval/services/llm_service.py
git commit -m "feat: add LLM service using Groq free tier inference"

git add backend/app/modules/retrieval/schemas/query.py backend/app/modules/retrieval/schemas/__init__.py
git commit -m "feat: add query request and answer response Pydantic schemas"

git add backend/app/modules/retrieval/services/answer_service.py
git commit -m "feat: add answer service orchestrating full RAG pipeline with hallucination guard"

git add backend/app/modules/retrieval/controllers/query_controller.py backend/app/modules/retrieval/controllers/__init__.py
git commit -m "feat: add query controller wiring answer service to POST /api/v1/query"

git add backend/tests/conftest.py
git commit -m "test: add CrossEncoder stub to conftest for unit test isolation"

git add backend/tests/unit/test_context_builder.py
git commit -m "test: add unit tests for context builder dedup and citation logic"

git add backend/tests/unit/test_hybrid_retrieval.py
git commit -m "test: add unit tests for RRF score merging in hybrid retrieval"

git add backend/tests/unit/test_reranking.py
git commit -m "test: add unit tests for cross-encoder reranking service"

git add backend/tests/unit/test_answer_service.py
git commit -m "test: add unit tests for hallucination guard in answer service"

git add backend/.env.example
git commit -m "chore: add GROQ_API_KEY to env template"

git add backend/app/modules/retrieval/__init__.py backend/app/modules/retrieval/services/__init__.py backend/app/modules/retrieval/repositories/__init__.py
git commit -m "chore: add retrieval module init files"

git add README.md
git commit -m "docs: update README roadmap to mark retrieval and answering complete"

echo ""
echo "Done. $(git log --oneline | wc -l) total commits."
echo "Review with: git log --oneline"
echo "Then push with: git push"
