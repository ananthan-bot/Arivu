#!/bin/bash
set -e

git add .gitignore
git commit -m "chore: add gitignore"

git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions workflow (lint + test)"

git add infrastructure/docker-compose.yml
git commit -m "chore: add docker-compose for postgres + backend"

git add backend/Dockerfile
git commit -m "chore: add backend Dockerfile"

git add backend/requirements.txt
git commit -m "chore: add backend dependencies"

git add backend/.env.example
git commit -m "chore: add env template"

git add backend/app/__init__.py backend/app/main.py
git commit -m "feat: add FastAPI app entrypoint with health check"

git add backend/app/core/__init__.py backend/app/core/config.py
git commit -m "feat: add pydantic-settings config"

git add backend/app/core/database.py
git commit -m "feat: add SQLAlchemy engine/session setup"

git add backend/app/modules/__init__.py backend/app/modules/ingestion/__init__.py backend/app/modules/ingestion/models/__init__.py backend/app/modules/ingestion/models/document.py
git commit -m "feat: add Document/Chunk ORM models with pgvector column"

git add backend/app/modules/ingestion/services/__init__.py backend/app/modules/ingestion/services/extraction.py
git commit -m "feat: add extraction service (pdf/txt/md)"

git add backend/app/modules/ingestion/services/chunking.py
git commit -m "feat: add heading-aware recursive chunking service"

git add backend/app/modules/ingestion/services/embedding.py
git commit -m "feat: add BGE embedding service"

git add backend/app/modules/ingestion/repositories/__init__.py backend/app/modules/ingestion/repositories/document_repository.py
git commit -m "feat: add document repository"

git add backend/app/modules/ingestion/services/ingestion_service.py
git commit -m "feat: add ingestion pipeline orchestration service"

git add backend/app/modules/ingestion/schemas/__init__.py backend/app/modules/ingestion/schemas/document.py backend/app/modules/ingestion/controllers/__init__.py backend/app/modules/ingestion/controllers/document_controller.py
git commit -m "feat: add document upload/list API endpoints"

git add backend/tests/__init__.py backend/tests/conftest.py backend/tests/unit backend/tests/integration
git commit -m "test: add unit + integration tests for ingestion pipeline"

git add backend/app/modules/retrieval
git commit -m "feat: add retrieval module skeleton and chunk repository"

git add backend/app/shared
git commit -m "chore: add shared module placeholder for cross-module utils"

echo ""
echo "Done. $(git log --oneline | wc -l) commits created."
echo "Review with: git log --oneline"
echo "Then push with: git push -u origin main"
