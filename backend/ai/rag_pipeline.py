import logging
import os
import re

from ai.chunking import chunk_text
from ai.embeddings import embed_text, embed_texts
from ai.ollama_service import LocalAIError, generate_chat_completion, generate_text, is_fallback_only
from ai.vector_store import (
    VectorStoreError,
    add_document_chunks,
    collection_document_count,
    list_indexed_chunks,
    search_similar_chunks,
)
from models.conversation import Message

logger = logging.getLogger(__name__)

STOPWORDS = {
    "about",
    "according",
    "does",
    "from",
    "have",
    "tell",
    "that",
    "the",
    "this",
    "what",
    "when",
    "where",
    "which",
    "with",
}


def _fallback_enabled() -> bool:
    value = os.getenv("AI_CHAT_FALLBACK_ENABLED", "false").strip().lower()
    return value in {"1", "true", "yes", "on"}


def _fallback_only() -> bool:
    return is_fallback_only()


def _fallback_answer(question: str) -> str:
    normalized = question.lower()
    if any(word in normalized for word in ("price", "pricing", "demo", "trial", "buy", "purchase")):
        return (
            "I can help with sales questions. Please share your company name, email, phone number, "
            "and what you want to use the support assistant for, and the team can follow up with pricing or a demo."
        )
    if any(word in normalized for word in ("login", "password", "sign in", "account")):
        return (
            "For login or account issues, first try resetting your password from the sign-in page. "
            "If that does not work, create a support ticket with your account email and the exact error message."
        )
    if any(word in normalized for word in ("refund", "payment", "billing", "charged", "invoice")):
        return (
            "For billing or payment issues, please create a support ticket with the transaction date, amount, "
            "invoice or payment reference, and the email used for the account."
        )
    return (
        "I can help with support questions, tickets, billing, login issues, and product guidance. "
        "Please share a few more details about the problem, including any error message and what you already tried."
    )


def _format_history(history: list[Message], limit: int = 8) -> str:
    if not history:
        return "No previous conversation."
    rows = history[-limit:]
    return "\n".join(
        f"{'Customer' if message.sender == 'user' else 'Assistant'}: {message.content}"
        for message in rows
    )


def _format_context(chunks: list[dict]) -> str:
    if not chunks:
        return "No relevant document context was found."
    lines: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        metadata = chunk.get("metadata") or {}
        filename = metadata.get("filename", "unknown document")
        lines.append(f"[Source {index}: {filename}]\n{chunk.get('text', '')}")
    return "\n\n".join(lines)


def _question_terms(question: str) -> set[str]:
    raw_terms = re.findall(r"[a-z0-9]+", question.lower())
    terms = {term for term in raw_terms if len(term) > 2 and term not in STOPWORDS}
    synonyms = {
        "timings": {"hours", "business", "available", "availability", "support"},
        "timing": {"hours", "business", "available", "availability", "support"},
        "hours": {"timings", "business", "available", "availability", "support"},
        "support": {"customer", "technical", "business", "hours", "available"},
        "services": {"service", "offered", "development", "automation", "cloud"},
        "service": {"services", "offered", "development", "automation", "cloud"},
        "pricing": {"price", "plan", "plans", "starter", "professional", "enterprise"},
        "price": {"pricing", "plan", "plans", "starter", "professional", "enterprise"},
        "plans": {"pricing", "price", "starter", "professional", "enterprise"},
        "technologies": {"technology", "python", "fastapi", "react", "node", "postgresql", "tensorflow", "aws"},
        "technology": {"technologies", "python", "fastapi", "react", "node", "postgresql", "tensorflow", "aws"},
        "internships": {"internship", "remote", "ai", "ml", "full", "stack"},
        "internship": {"internships", "remote", "ai", "ml", "full", "stack"},
        "skills": {"skill", "technical", "programming", "tools", "concepts", "python", "sql"},
        "skill": {"skills", "technical", "programming", "tools", "concepts", "python", "sql"},
        "projects": {"project", "built", "developed", "analysis", "prediction", "forecasting"},
        "project": {"projects", "built", "developed", "analysis", "prediction", "forecasting"},
        "education": {"degree", "graduation", "university", "btech", "college"},
        "degree": {"education", "graduation", "university", "btech", "college"},
        "resume": {"summary", "education", "projects", "skills", "certifications"},
    }
    expanded = set(terms)
    for term in terms:
        expanded.update(synonyms.get(term, set()))
    return expanded


def _chunk_key(row: dict) -> tuple:
    metadata = row.get("metadata") or {}
    document_id = metadata.get("document_id")
    chunk_index = metadata.get("chunk_index")
    if document_id is not None and chunk_index is not None:
        return ("chunk", document_id, chunk_index)
    return ("text", str(row.get("text", ""))[:200])


def _lexical_score(question: str, text: str) -> int:
    terms = _question_terms(question)
    haystack = set(re.findall(r"[a-z0-9]+", text.lower()))
    return len(terms & haystack)


def _relevant_pdf_excerpts(question: str, chunks: list[dict], *, limit: int = 8) -> str:
    terms = _question_terms(question)
    scored: list[tuple[int, str]] = []
    seen: set[str] = set()
    for chunk in chunks:
        lines = [line.strip() for line in str(chunk.get("text", "")).splitlines() if line.strip()]
        for index, line in enumerate(lines):
            haystack = set(re.findall(r"[a-z0-9]+", line.lower()))
            score = len(terms & haystack)
            if score == 0:
                continue
            excerpt_lines = [line]
            if index + 1 < len(lines):
                excerpt_lines.append(lines[index + 1])
            if index + 2 < len(lines) and score >= 2:
                excerpt_lines.append(lines[index + 2])
            excerpt = " ".join(excerpt_lines)
            normalized = " ".join(excerpt.lower().split())
            if normalized in seen:
                continue
            seen.add(normalized)
            scored.append((score, excerpt))
    scored.sort(key=lambda item: item[0], reverse=True)
    excerpts = [excerpt for _, excerpt in scored[:limit]]
    return "\n".join(f"- {excerpt}" for excerpt in excerpts)


def _looks_like_missing_context(answer: str) -> bool:
    normalized = answer.lower()
    return any(
        phrase in normalized
        for phrase in (
            "context does not",
            "context provided does not",
            "cannot answer this question from the provided context",
            "could not find that",
            "does not provide any information",
            "unable to provide",
            "unable to access external sources",
        )
    )


def _looks_like_prompt_leak(answer: str) -> bool:
    normalized = answer.lower()
    return any(
        phrase in normalized
        for phrase in (
            "you are an ai assistant",
            "your task is to answer",
            "based on the context below",
            "customer question:",
            "company pdf context:",
        )
    )


def _combined_chunk_text(chunks: list[dict]) -> str:
    return "\n".join(str(chunk.get("text", "")) for chunk in chunks)


def _compact_pdf_text(text: str) -> str:
    return " ".join(text.split())


def _capture_between(text: str, start: str, stops: tuple[str, ...]) -> str | None:
    pattern = re.escape(start) + r"\s*(.*?)"
    if stops:
        pattern += r"(?=" + "|".join(re.escape(stop) for stop in stops) + r"|$)"
    else:
        pattern += r"$"
    match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    value = _compact_pdf_text(match.group(1))
    return value or None


def _known_section_titles(text: str) -> list[str]:
    titles: list[str] = []
    for line in text.splitlines():
        clean = line.strip().strip(":")
        if not clean or len(clean) > 60:
            continue
        if clean.isupper() or re.fullmatch(r"[A-Z][A-Za-z0-9 &/,+-]{2,}", clean):
            titles.append(clean)
    return list(dict.fromkeys(titles))


def _section_answer(question: str, chunks: list[dict]) -> str | None:
    terms = _question_terms(question)
    full_text = _combined_chunk_text(chunks)
    compact_text = _compact_pdf_text(full_text)
    section_aliases = {
        "skills": {"skill", "skills", "technologies", "technology", "tools"},
        "projects": {"project", "projects", "portfolio", "built"},
        "education": {"education", "degree", "graduation", "university", "college"},
        "experience": {"experience", "work", "internship", "internships", "employment"},
        "certifications": {"certification", "certifications", "certificate", "certificates"},
        "pricing": {"price", "pricing", "plans", "plan"},
        "services": {"service", "services", "offered", "offerings"},
    }
    requested_sections = [
        title for title, aliases in section_aliases.items() if aliases & terms
    ]
    if not requested_sections:
        return None

    titles = _known_section_titles(full_text)
    if not titles:
        titles = [section.upper() for section in section_aliases]
    stops = tuple(titles)
    answers: list[str] = []
    for section in requested_sections:
        candidate_titles = [
            title
            for title in titles
            if section in title.lower() or any(alias in title.lower() for alias in section_aliases[section])
        ]
        for title in candidate_titles or [section.upper(), section.title(), section.capitalize()]:
            value = _capture_between(compact_text, title, tuple(stop for stop in stops if stop.lower() != title.lower()))
            if value:
                answers.append(f"{section.title()}: {value}")
                break
    if not answers:
        return None
    return "Based on the uploaded PDF: " + "; ".join(dict.fromkeys(answers)) + "."


def _extractive_pdf_answer(question: str, chunks: list[dict]) -> str | None:
    excerpts = _relevant_pdf_excerpts(question, chunks)
    if not excerpts.strip():
        return None

    section_answer = _section_answer(question, chunks)
    if section_answer:
        return section_answer

    excerpt_lines = [line[2:].strip() for line in excerpts.splitlines() if line.startswith("- ")]
    selected = []
    for line in excerpt_lines:
        if line not in selected:
            selected.append(line)
        if len(selected) >= 2:
            break
    if not selected:
        return None
    return "Based on the uploaded PDF: " + " ".join(selected)


def _grounded_user_prompt(question: str, chunks: list[dict]) -> str:
    if not chunks:
        return question
    excerpts = _relevant_pdf_excerpts(question, chunks)
    excerpt_section = f"Most relevant lines extracted from the PDF:\n{excerpts}\n\n" if excerpts else ""
    return (
        "Answer the customer question using only the company PDF context below. "
        "Do not use canned support replies. Do not say the context is missing when the answer is present. "
        "Treat support timings, support hours, working hours, and business hours as the same kind of question. "
        "If the answer is not in the context, say: I could not find that in the uploaded company documents.\n\n"
        f"{excerpt_section}"
        f"Company PDF context:\n{_format_context(chunks)}\n\n"
        f"Customer question: {question}\n\n"
        "Answer:"
    )


async def ingest_document(*, document_id: int, filename: str, text: str) -> int:
    chunks = chunk_text(text)
    if not chunks:
        raise LocalAIError("No indexable text was found in the document.")
    embeddings = await embed_texts(chunks)
    try:
        add_document_chunks(document_id=document_id, chunks=chunks, embeddings=embeddings, filename=filename)
    except VectorStoreError as exc:
        raise LocalAIError(str(exc)) from exc
    return len(chunks)


async def retrieve_context(question: str, *, limit: int = 5) -> list[dict]:
    if collection_document_count() == 0:
        logger.info("rag_retrieval_skipped_empty_collection")
        return []
    query_embedding = await embed_text(question)
    try:
        vector_rows = search_similar_chunks(query_embedding=query_embedding, limit=max(limit, 10))
        all_rows = list_indexed_chunks()
    except VectorStoreError as exc:
        raise LocalAIError(str(exc)) from exc
    max_distance = float(os.getenv("RAG_MAX_CONTEXT_DISTANCE", "0.60"))
    merged: dict[tuple, dict] = {}
    for row in all_rows:
        merged[_chunk_key(row)] = row
    for row in vector_rows:
        merged[_chunk_key(row)] = row
    rows = list(merged.values())
    relevant_rows = [
        row
        for row in rows
        if (
            (row.get("distance") is not None and float(row["distance"]) <= max_distance)
            or _lexical_score(question, str(row.get("text", ""))) >= 2
        )
    ]
    relevant_rows.sort(
        key=lambda row: (
            -_lexical_score(question, str(row.get("text", ""))),
            float(row["distance"]) if row.get("distance") is not None else 999.0,
        )
    )
    relevant_rows = relevant_rows[:limit]
    if rows and not relevant_rows:
        logger.info(
            "rag_retrieval_discarded_low_relevance",
            extra={"best_distance": rows[0].get("distance"), "max_distance": max_distance},
        )
    return relevant_rows


async def generate_grounded_answer(*, question: str, history: list[Message]) -> str:
    if _fallback_only():
        return _fallback_answer(question)

    try:
        chunks = await retrieve_context(question)
    except LocalAIError as exc:
        chunks = []
        logger.warning("rag_retrieval_failed_using_llm_without_context", extra={"error": str(exc)})

    history_limit = int(os.getenv("OLLAMA_HISTORY_LIMIT", "12"))
    system = (
        "You are a customer support assistant for a SaaS platform. "
        "For company-specific questions, answer from the uploaded company document context. "
        "Document context is more authoritative than "
        "older conversation messages or older assistant answers. If an older assistant answer conflicts "
        "with the document context, correct it. Do not invent document facts. "
        "If no relevant document context is provided, say that you could not find the answer in the uploaded documents. "
        "Keep answers concise and practical, usually two short sentences or fewer. Do not use numbered lists. "
        "Cite labels like [Source 1] only when using retrieved context."
    )

    messages: list[dict[str, str]] = [{"role": "system", "content": system}]
    if chunks:
        history = [message for message in history if message.sender == "user"]
    for message in history[-history_limit:]:
        role = "user" if message.sender == "user" else "assistant"
        messages.append({"role": role, "content": message.content})
    messages.append({"role": "user", "content": _grounded_user_prompt(question, chunks)})

    use_chat_api = os.getenv("OLLAMA_USE_CHAT_API", "true").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    try:
        if use_chat_api:
            answer = await generate_chat_completion(messages)
            if chunks and (_looks_like_missing_context(answer) or _looks_like_prompt_leak(answer)):
                pdf_answer = _extractive_pdf_answer(question, chunks)
                if pdf_answer:
                    return pdf_answer
            return answer
        prompt = (
            f"{system}\n\nConversation history:\n{_format_history(history)}\n\n"
            f"Customer question: {question}\nGrounded answer:"
        )
        answer = await generate_text(prompt)
        if chunks and (_looks_like_missing_context(answer) or _looks_like_prompt_leak(answer)):
            pdf_answer = _extractive_pdf_answer(question, chunks)
            if pdf_answer:
                return pdf_answer
        return answer
    except LocalAIError:
        if not _fallback_enabled():
            raise
        logger.warning("rag_generation_failed_using_fallback")
        return _fallback_answer(question)
