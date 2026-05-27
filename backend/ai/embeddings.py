from ai.ollama_service import generate_embedding


async def embed_text(text: str) -> list[float]:
    return await generate_embedding(text)


async def embed_texts(texts: list[str]) -> list[list[float]]:
    embeddings: list[list[float]] = []
    for text in texts:
        embeddings.append(await embed_text(text))
    return embeddings
