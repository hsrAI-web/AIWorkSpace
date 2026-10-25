from __future__ import annotations

import json
import math
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from langchain_openai import OpenAIEmbeddings

KNOWLEDGE_BASE = Path(__file__).with_name("knowledge-base.json")
EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-8B"
SIMILARITY_THRESHOLD = 0.35
RELEVANCE_WINDOW = 0.03


@lru_cache(maxsize=1)
def _documents() -> tuple[dict[str, Any], ...]:
    payload = json.loads(KNOWLEDGE_BASE.read_text(encoding="utf-8"))
    reviewed_at = payload["reviewedAt"]
    documents = payload["documents"]
    ids: set[str] = set()
    for document in documents:
        if document["id"] in ids or not document["url"].startswith("https://"):
            raise ValueError("The public knowledge corpus has duplicate IDs or an unsafe source URL.")
        ids.add(document["id"])
        document["reviewedAt"] = reviewed_at
    return tuple(documents)


@lru_cache(maxsize=1)
def _embeddings() -> OpenAIEmbeddings:
    api_key = os.getenv("NEBIUS_API_KEY")
    if not api_key:
        raise RuntimeError("NEBIUS_API_KEY is required for semantic knowledge retrieval.")
    return OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=api_key,
        base_url="https://api.tokenfactory.nebius.com/v1",
        request_timeout=20,
        max_retries=1,
        check_embedding_ctx_length=False,
    )


@lru_cache(maxsize=1)
def _document_vectors() -> tuple[tuple[dict[str, Any], tuple[float, ...]], ...]:
    documents = _documents()
    vectors = _embeddings().embed_documents([
        f'{document["title"]}\nTopics: {", ".join(document["topics"])}\n{document["content"]}'
        for document in documents
    ])
    if len(vectors) != len(documents) or not vectors or any(len(vector) != len(vectors[0]) for vector in vectors):
        raise RuntimeError("The semantic index returned an invalid vector set.")
    return tuple((document, tuple(float(value) for value in vector)) for document, vector in zip(documents, vectors))


def _cosine_similarity(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if len(left) != len(right) or not left:
        return 0.0
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if not left_norm or not right_norm:
        return 0.0
    return sum(a * b for a, b in zip(left, right)) / (left_norm * right_norm)


def search_public_knowledge(query: str, limit: int = 3) -> dict[str, Any]:
    query = query.strip()
    if not query:
        return {"ok": True, "found": False, "documents": [], "sources": [], "message": "Enter a knowledge question."}
    if not 1 <= limit <= 5:
        raise ValueError("Knowledge result limit must be between 1 and 5.")

    try:
        vectors = _document_vectors()
        retrieval_query = f"Instruct: Retrieve public guidance that answers the question.\nQuery: {query}"
        query_vector = tuple(float(value) for value in _embeddings().embed_query(retrieval_query))
    except Exception:
        return {
            "ok": False,
            "found": False,
            "documents": [],
            "sources": [],
            "message": "Public-source semantic retrieval is temporarily unavailable. Do not answer from model memory.",
        }

    ranked = sorted(
        ((document, _cosine_similarity(query_vector, vector)) for document, vector in vectors),
        key=lambda item: item[1],
        reverse=True,
    )
    minimum_score = max(SIMILARITY_THRESHOLD, ranked[0][1] - RELEVANCE_WINDOW) if ranked else SIMILARITY_THRESHOLD
    relevant = [(document, score) for document, score in ranked if score >= minimum_score][:limit]
    if not relevant:
        return {
            "ok": True,
            "found": False,
            "documents": [],
            "sources": [],
            "message": "No relevant document was found in the curated public reference library.",
        }

    sources = [
        {
            "label": f'Public reference · {document["publisher"]} · {document["title"]}',
            "timestamp": document["reviewedAt"],
            "url": document["url"],
        }
        for document, _score in relevant
    ]
    return {
        "ok": True,
        "found": True,
        "disclaimer": "These are curated public references, not the company's policy, product claims, internal assets, or live release status.",
        "documents": [
            {
                "title": document["title"],
                "publisher": document["publisher"],
                "publishedAt": document["publishedAt"],
                "content": document["content"],
                "similarity": round(score, 3),
            }
            for document, score in relevant
        ],
        "sources": sources,
    }
