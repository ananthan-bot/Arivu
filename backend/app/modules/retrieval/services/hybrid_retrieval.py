"""
Hybrid retrieval: combines dense vector search with BM25 keyword search
using Reciprocal Rank Fusion (RRF).

Why RRF: vector similarity (cosine distance) and BM25 scores live on
completely different, incomparable scales -- you can't average a cosine
distance with a BM25 score directly. RRF sidesteps this by working purely
off *rank position* in each list rather than the raw scores, which is why
it's the standard fusion technique in real hybrid search systems (this is
the same approach Elasticsearch's hybrid search uses under the hood).

A chunk that ranks well in either list gets a boost; one that ranks well
in both wins.
"""
from rank_bm25 import BM25Okapi

from app.core.config import get_settings
from app.modules.ingestion.services.embedding import EmbeddingService
from app.modules.retrieval.repositories.chunk_repository import ChunkRecord, ChunkRepository

settings = get_settings()

RRF_K = 60  # standard constant from the original RRF paper


class HybridRetrievalService:
    def __init__(self, repo: ChunkRepository, embedder: EmbeddingService):
        self.repo = repo
        self.embedder = embedder

    def retrieve(self, query: str, top_k: int) -> list[tuple[ChunkRecord, float]]:
        candidate_pool_size = min(top_k * 3, settings.top_k_candidates)

        vector_ranked = self._vector_rank(query, candidate_pool_size)
        bm25_ranked = self._bm25_rank(query, candidate_pool_size)

        fused_scores: dict[str, float] = {}
        chunk_lookup: dict[str, ChunkRecord] = {}

        for rank, chunk in enumerate(vector_ranked):
            key = str(chunk.id)
            chunk_lookup[key] = chunk
            fused_scores[key] = fused_scores.get(key, 0.0) + 1.0 / (RRF_K + rank + 1)

        for rank, chunk in enumerate(bm25_ranked):
            key = str(chunk.id)
            chunk_lookup[key] = chunk
            fused_scores[key] = fused_scores.get(key, 0.0) + 1.0 / (RRF_K + rank + 1)

        ranked_keys = sorted(fused_scores.keys(), key=lambda k: fused_scores[k], reverse=True)

        return [(chunk_lookup[key], fused_scores[key]) for key in ranked_keys[:top_k]]

    def _vector_rank(self, query: str, top_k: int) -> list[ChunkRecord]:
        query_embedding = self.embedder.embed_query(query)
        results = self.repo.vector_search(query_embedding, top_k=top_k)
        return [chunk for chunk, _distance in results]

    def _bm25_rank(self, query: str, top_k: int) -> list[ChunkRecord]:
        all_chunks = self.repo.get_all_ready_chunks()
        if not all_chunks:
            return []

        tokenized_corpus = [c.text.lower().split() for c in all_chunks]
        bm25 = BM25Okapi(tokenized_corpus)

        tokenized_query = query.lower().split()
        scores = bm25.get_scores(tokenized_query)

        scored_chunks = sorted(zip(all_chunks, scores), key=lambda pair: pair[1], reverse=True)
        return [chunk for chunk, _score in scored_chunks[:top_k]]
