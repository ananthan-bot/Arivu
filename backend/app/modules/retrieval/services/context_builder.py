"""
Builds the final context block handed to the LLM from reranked chunks.

Three jobs, in order:
1. Drop near-duplicate chunks -- two chunks that say almost the same thing
   waste context budget and dilute the answer without adding information.
2. Truncate to a token budget -- blindly concatenating every chunk risks
   exceeding the model's context window or paying for tokens that don't
   improve the answer.
3. Format each surviving chunk with a citation marker ([1], [2], ...) so
   the LLM can reference specific sources in its answer, and so we can map
   those markers back to (document, page) for the citation engine.
"""
from dataclasses import dataclass

from app.core.config import get_settings
from app.modules.retrieval.repositories.chunk_repository import ChunkRecord

settings = get_settings()

# Same word-based estimate used in chunking -- see chunking.py for rationale
# (avoids an unnecessary external dependency on tiktoken's encoding download).
_WORDS_PER_TOKEN = 0.75

# A simple word-overlap threshold is enough to catch near-duplicate chunks
# without pulling in a second embedding comparison at this stage.
_DUPLICATE_OVERLAP_THRESHOLD = 0.8


def _token_len(text: str) -> int:
    return int(len(text.split()) / _WORDS_PER_TOKEN)


def _word_overlap_ratio(a: str, b: str) -> float:
    words_a = set(a.lower().split())
    words_b = set(b.lower().split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    smaller = min(len(words_a), len(words_b))
    return len(intersection) / smaller


@dataclass
class ContextChunk:
    marker: str  # e.g. "[1]"
    chunk: ChunkRecord
    score: float


@dataclass
class BuiltContext:
    context_text: str  # formatted block ready to inject into the LLM prompt
    chunks: list[ContextChunk]  # for mapping citations back to sources
    top_score: float  # highest reranker score among surviving chunks -- used by the hallucination guard


class ContextBuilder:
    def build(
        self,
        ranked_chunks: list[tuple[ChunkRecord, float]],
        max_tokens: int = 2000,
    ) -> BuiltContext:
        if not ranked_chunks:
            return BuiltContext(context_text="", chunks=[], top_score=0.0)

        deduplicated = self._deduplicate(ranked_chunks)

        selected: list[ContextChunk] = []
        used_tokens = 0
        for i, (chunk, score) in enumerate(deduplicated, start=1):
            chunk_tokens = _token_len(chunk.text)
            if used_tokens + chunk_tokens > max_tokens:
                break
            selected.append(ContextChunk(marker=f"[{i}]", chunk=chunk, score=score))
            used_tokens += chunk_tokens

        context_text = "\n\n".join(
            f"{c.marker} (source: {c.chunk.filename}"
            f"{f', page {c.chunk.page}' if c.chunk.page else ''}"
            f"{f', {c.chunk.heading}' if c.chunk.heading else ''}):\n{c.chunk.text}"
            for c in selected
        )

        top_score = selected[0].score if selected else 0.0
        return BuiltContext(context_text=context_text, chunks=selected, top_score=top_score)

    def _deduplicate(
        self, ranked_chunks: list[tuple[ChunkRecord, float]]
    ) -> list[tuple[ChunkRecord, float]]:
        kept: list[tuple[ChunkRecord, float]] = []
        for chunk, score in ranked_chunks:
            is_duplicate = any(
                _word_overlap_ratio(chunk.text, kept_chunk.text) >= _DUPLICATE_OVERLAP_THRESHOLD
                for kept_chunk, _ in kept
            )
            if not is_duplicate:
                kept.append((chunk, score))
        return kept
