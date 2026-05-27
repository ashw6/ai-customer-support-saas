import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import chromadb


class VectorStoreError(RuntimeError):
    pass


COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "support_documents")
DEFAULT_CHROMA_DIR = Path(__file__).resolve().parents[1] / "chroma_db"


@lru_cache(maxsize=1)
def _client():
    path = os.getenv("CHROMA_DB_DIR", str(DEFAULT_CHROMA_DIR))
    return chromadb.PersistentClient(path=path)


@lru_cache(maxsize=1)
def _collection():
    try:
        return _client().get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    except Exception as exc:
        raise VectorStoreError("Could not initialize the local vector database.") from exc


def add_document_chunks(
    *,
    document_id: int,
    chunks: list[str],
    embeddings: list[list[float]],
    filename: str,
) -> None:
    if not chunks:
        return
    if len(chunks) != len(embeddings):
        raise VectorStoreError("Chunk and embedding counts do not match.")
    ids = [f"doc-{document_id}-chunk-{index}" for index in range(len(chunks))]
    metadatas = [
        {"document_id": document_id, "chunk_index": index, "filename": filename}
        for index in range(len(chunks))
    ]
    try:
        _collection().upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )
    except Exception as exc:
        raise VectorStoreError("Could not store document embeddings.") from exc


def collection_document_count() -> int:
    """Number of indexed chunks in the vector collection (0 when empty / unavailable)."""
    try:
        return int(_collection().count())
    except Exception:
        return 0


def search_similar_chunks(*, query_embedding: list[float], limit: int = 5) -> list[dict[str, Any]]:
    if limit < 1:
        return []
    try:
        result = _collection().query(query_embeddings=[query_embedding], n_results=limit)
    except Exception as exc:
        raise VectorStoreError("Could not search document embeddings.") from exc
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]
    rows: list[dict[str, Any]] = []
    for index, document in enumerate(documents):
        rows.append(
            {
                "text": document,
                "metadata": metadatas[index] if index < len(metadatas) else {},
                "distance": distances[index] if index < len(distances) else None,
            }
        )
    return rows


def list_indexed_chunks(*, limit: int = 500) -> list[dict[str, Any]]:
    try:
        result = _collection().get(limit=limit, include=["documents", "metadatas"])
    except Exception as exc:
        raise VectorStoreError("Could not load indexed document chunks.") from exc
    documents = result.get("documents", [])
    metadatas = result.get("metadatas", [])
    rows: list[dict[str, Any]] = []
    for index, document in enumerate(documents):
        rows.append(
            {
                "text": document,
                "metadata": metadatas[index] if index < len(metadatas) else {},
                "distance": None,
            }
        )
    return rows


def delete_document_chunks(document_id: int) -> None:
    try:
        _collection().delete(where={"document_id": document_id})
    except Exception as exc:
        raise VectorStoreError("Could not delete document embeddings.") from exc
