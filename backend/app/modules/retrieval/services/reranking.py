"""
Cross-encoder reranking: narrows the top-N hybrid-retrieval candidates down
to the top-K most relevant chunks.

Why a second stage at all: the hybrid retrieval step (RRF over vector +
BM25) is cheap but approximate -- it scores the query and each chunk
*separately* and compares them afterward. A cross-encoder instead feeds the
query and chunk together into one model pass, so it can directly judge
"does this chunk actually answer this query" rather than "are these two
independently-computed vectors similar." That's more accurate but far too
slow to run over an entire corpus, which is why it only runs on the small
candidate set the first stage already narrowed down -- the standard
retrieve-then-rerank pattern used in production search systems.
"""
from functools import lru_cache

from sentence_transformers import CrossEncoder

from app.modules.retrieval.repositories.chunk_repository import ChunkRecord

CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


@lru_cache
def _get_cross_encoder() -> CrossEncoder:
    """Loaded once per process -- model load is expensive, scoring calls aren't."""
    return CrossEncoder(CROSS_ENCODER_MODEL)


class RerankingService:
    def rerank(
        self,
        query: str,
        candidates: list[tuple[ChunkRecord, float]],
        top_k: int,
    ) -> list[tuple[ChunkRecord, float]]:
        if not candidates:
            return []

        model = _get_cross_encoder()
        pairs = [[query, chunk.text] for chunk, _ in candidates]
        scores = model.predict(pairs)

        reranked = sorted(
            zip([chunk for chunk, _ in candidates], scores),
            key=lambda pair: pair[1],
            reverse=True,
        )
        return [(chunk, float(score)) for chunk, score in reranked[:top_k]]
