"""LLM service using Groq free tier for answer generation."""
import logging
import os

import httpx

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """You are Arivu, an enterprise knowledge assistant. Answer the user's question using ONLY the numbered context passages provided below.

Rules:
- Cite every factual claim using the passage marker it came from, e.g. [1] or [2].
- If the context does not contain enough information to answer confidently, say so plainly rather than guessing or using outside knowledge.
- Do not invent citations. Only cite markers that appear in the context.
- Be concise and directly answer the question asked."""


class LLMService:
    def generate_answer(self, query: str, context_text: str) -> str:
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set in environment.")

        user_message = f"Context:\n{context_text}\n\nQuestion: {query}"

        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            "max_tokens": 1024,
        }

        logger.info("Sending request to Groq with model: %s", GROQ_MODEL)

        response = httpx.post(
            GROQ_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30.0,
        )

        if not response.is_success:
            logger.error("Groq error %s: %s", response.status_code, response.text)
            raise ValueError(f"Groq API error {response.status_code}: {response.text}")

        return response.json()["choices"][0]["message"]["content"]
