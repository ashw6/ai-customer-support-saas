import re


def chunk_text(text: str, *, chunk_size: int = 1200, overlap: int = 180) -> list[str]:
    normalized = re.sub(r"[ \t]+", " ", text)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized).strip()
    if not normalized:
        return []
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        window = normalized[start:end]
        if end < len(normalized):
            boundary = max(
                window.rfind("\n\n"),
                window.rfind(". "),
                window.rfind("? "),
                window.rfind("! "),
                window.rfind("; "),
            )
            if boundary > chunk_size * 0.5:
                end = start + boundary + 1
                window = normalized[start:end]
        chunks.append(window.strip())
        if end >= len(normalized):
            break
        next_start = max(end - overlap, start + 1)
        boundary = max(
            normalized.rfind("\n\n", next_start, end),
            normalized.rfind(". ", next_start, end),
            normalized.rfind("? ", next_start, end),
            normalized.rfind("! ", next_start, end),
            normalized.rfind("; ", next_start, end),
        )
        if boundary >= next_start:
            next_start = boundary + 1
        start = next_start
    return [chunk for chunk in chunks if chunk]
