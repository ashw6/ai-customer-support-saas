import os
from dataclasses import dataclass
from urllib.parse import urlparse, urlunparse

import httpx


class LocalAIError(RuntimeError):
    pass


@dataclass(frozen=True)
class OllamaConfig:
    generate_url: str
    embeddings_url: str
    chat_model: str
    embedding_model: str
    timeout_seconds: float
    num_predict: int


@dataclass(frozen=True)
class OpenAIConfig:
    api_key: str
    base_url: str
    chat_model: str
    embedding_model: str
    timeout_seconds: float
    max_tokens: int


def _truthy(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def is_fallback_only() -> bool:
    return _truthy("AI_CHAT_FALLBACK_ONLY")


def ai_provider() -> str:
    return os.getenv("AI_PROVIDER", "ollama").strip().lower()


def get_ollama_config() -> OllamaConfig:
    return OllamaConfig(
        generate_url=os.getenv("OLLAMA_GENERATE_URL", "http://localhost:11434/api/generate"),
        embeddings_url=os.getenv("OLLAMA_EMBEDDINGS_URL", "http://localhost:11434/api/embeddings"),
        chat_model=os.getenv("OLLAMA_CHAT_MODEL", os.getenv("OLLAMA_MODEL", "mistral")),
        embedding_model=os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"),
        timeout_seconds=float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120")),
        num_predict=int(os.getenv("OLLAMA_NUM_PREDICT", "120")),
    )


def get_openai_config() -> OpenAIConfig:
    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not api_key:
        raise LocalAIError("OPENAI_API_KEY is not configured.")
    return OpenAIConfig(
        api_key=api_key,
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
        chat_model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        timeout_seconds=float(os.getenv("OPENAI_TIMEOUT_SECONDS", os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))),
        max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", os.getenv("OLLAMA_NUM_PREDICT", "180"))),
    )


def _chat_url(generate_url: str) -> str:
    explicit = (os.getenv("OLLAMA_CHAT_URL") or "").strip()
    if explicit:
        return explicit
    if generate_url.rstrip("/").endswith("/api/generate"):
        return generate_url.rstrip("/")[: -len("/api/generate")] + "/api/chat"
    parsed = urlparse(generate_url)
    return urlunparse(parsed._replace(path="/api/chat"))


def _embed_fallback_url(embeddings_url: str) -> str:
    """Map legacy /api/embeddings to Ollama's /api/embed when needed."""
    parsed = urlparse(embeddings_url)
    if parsed.path.rstrip("/").endswith("embeddings"):
        path = parsed.path.rstrip("/").rsplit("/", 1)[0] + "/embed"
        return urlunparse(parsed._replace(path=path))
    return embeddings_url


async def _post_json(url: str, payload: dict, timeout_seconds: float) -> dict:
    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise LocalAIError("Local AI request timed out. Please try again.") from exc
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text.strip()[:300]
        message = f"Ollama returned HTTP {exc.response.status_code}."
        if detail:
            message = f"{message} {detail}"
        raise LocalAIError(message) from exc
    except httpx.RequestError as exc:
        raise LocalAIError("Could not reach Ollama. Is the local Ollama server running?") from exc

    try:
        return response.json()
    except ValueError as exc:
        raise LocalAIError("Ollama returned an invalid JSON response.") from exc


async def _post_openai_json(path: str, payload: dict, cfg: OpenAIConfig) -> dict:
    try:
        async with httpx.AsyncClient(timeout=cfg.timeout_seconds) as client:
            response = await client.post(
                f"{cfg.base_url}/{path.lstrip('/')}",
                json=payload,
                headers={
                    "Authorization": f"Bearer {cfg.api_key}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise LocalAIError("Hosted AI request timed out. Please try again.") from exc
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text.strip()[:300]
        message = f"Hosted AI returned HTTP {exc.response.status_code}."
        if detail:
            message = f"{message} {detail}"
        raise LocalAIError(message) from exc
    except httpx.RequestError as exc:
        raise LocalAIError("Could not reach the hosted AI provider.") from exc

    try:
        return response.json()
    except ValueError as exc:
        raise LocalAIError("Hosted AI returned an invalid JSON response.") from exc


async def generate_chat_completion(
    messages: list[dict[str, str]],
    *,
    config: OllamaConfig | None = None,
) -> str:
    """Generate a chat response with the configured AI provider."""
    if ai_provider() == "openai":
        cfg = get_openai_config()
        data = await _post_openai_json(
            "chat/completions",
            {
                "model": cfg.chat_model,
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": cfg.max_tokens,
            },
            cfg,
        )
        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            message = choices[0].get("message") if isinstance(choices[0], dict) else None
            if isinstance(message, dict):
                text = str(message.get("content", "")).strip()
                if text:
                    return text
        raise LocalAIError("Hosted AI returned an empty chat response.")

    cfg = config or get_ollama_config()
    data = await _post_json(
        _chat_url(cfg.generate_url),
        {
            "model": cfg.chat_model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": cfg.num_predict},
        },
        cfg.timeout_seconds,
    )
    message = data.get("message")
    if isinstance(message, dict):
        text = str(message.get("content", "")).strip()
        if text:
            return text
    raise LocalAIError("Ollama returned an empty chat response.")


async def check_ai_reachable() -> bool:
    if is_fallback_only():
        return True
    if ai_provider() == "openai":
        try:
            cfg = get_openai_config()
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{cfg.base_url}/models",
                    headers={"Authorization": f"Bearer {cfg.api_key}"},
                )
                return response.status_code < 500
        except (LocalAIError, httpx.HTTPError):
            return False
    return await check_ollama_reachable()


async def check_ollama_reachable(*, config: OllamaConfig | None = None) -> bool:
    cfg = config or get_ollama_config()
    base = _chat_url(cfg.generate_url).rsplit("/api/", 1)[0]
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{base}/api/tags")
            return response.status_code == 200
    except httpx.HTTPError:
        return False


async def generate_text(prompt: str, *, config: OllamaConfig | None = None) -> str:
    if ai_provider() == "openai":
        return await generate_chat_completion([{"role": "user", "content": prompt}])

    cfg = config or get_ollama_config()
    data = await _post_json(
        cfg.generate_url,
        {
            "model": cfg.chat_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": cfg.num_predict},
        },
        cfg.timeout_seconds,
    )
    text = str(data.get("response", "")).strip()
    if not text:
        raise LocalAIError("Ollama returned an empty response.")
    return text


def _parse_embedding_payload(data: dict) -> list[float]:
    embedding = data.get("embedding")
    if isinstance(embedding, list) and embedding:
        return [float(value) for value in embedding]
    embeddings = data.get("embeddings")
    if isinstance(embeddings, list) and embeddings:
        first = embeddings[0]
        if isinstance(first, list) and first:
            return [float(value) for value in first]
    raise LocalAIError("Ollama returned an empty embedding.")


async def generate_embedding(text: str, *, config: OllamaConfig | None = None) -> list[float]:
    if ai_provider() == "openai":
        cfg = get_openai_config()
        data = await _post_openai_json(
            "embeddings",
            {"model": cfg.embedding_model, "input": text},
            cfg,
        )
        rows = data.get("data")
        if isinstance(rows, list) and rows:
            embedding = rows[0].get("embedding") if isinstance(rows[0], dict) else None
            if isinstance(embedding, list) and embedding:
                return [float(value) for value in embedding]
        raise LocalAIError("Hosted AI returned an empty embedding.")

    cfg = config or get_ollama_config()
    legacy_payload = {"model": cfg.embedding_model, "prompt": text}
    try:
        data = await _post_json(cfg.embeddings_url, legacy_payload, cfg.timeout_seconds)
        return _parse_embedding_payload(data)
    except LocalAIError as exc:
        if "404" not in str(exc):
            raise
    modern_url = _embed_fallback_url(cfg.embeddings_url)
    modern_payload = {"model": cfg.embedding_model, "input": text}
    data = await _post_json(modern_url, modern_payload, cfg.timeout_seconds)
    return _parse_embedding_payload(data)
