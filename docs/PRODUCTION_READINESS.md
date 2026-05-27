# Production Readiness Checklist

This checklist is for preparing the project before a recruiter review, client handoff, or real deployment.

## Verified Locally

- Frontend tests pass with `npm test`.
- Frontend production build passes with `npm run build`.
- Backend tests pass with `python -m pytest tests`.
- Backend app imports successfully when required environment variables are set.

## Environment

- `ENVIRONMENT=production` is set outside local development.
- `DATABASE_URL` points to a managed PostgreSQL database.
- `JWT_SECRET` is unique per environment and at least 32 characters.
- `CORS_ORIGINS` contains only real HTTPS frontend origins in production.
- `FRONTEND_URL` matches the public frontend URL used in email links.
- Email credentials are optional, but configured when password reset and lead follow-up emails are expected.
- For a simple portfolio deployment, set `AI_CHAT_FALLBACK_ONLY=true`.
- For real document-grounded AI in production, either set `AI_PROVIDER=openai` with `OPENAI_API_KEY`, or set hosted `OLLAMA_GENERATE_URL` and `OLLAMA_EMBEDDINGS_URL` values that are reachable from the backend host.

## Backend

- Alembic migrations are run before serving traffic. The Render blueprint uses `preDeployCommand: python -m alembic upgrade head`.
- API health check responds at `/health`.
- `/docs` is reviewed for route clarity before demos.
- Request IDs are visible in API responses through `X-Request-ID`.
- Structured logs are enabled through `LOG_LEVEL`.
- AI provider failures return controlled errors instead of crashing the app.
- Email failures are logged and do not block core account/ticket flows.
- Backend tests use an isolated SQLite database so verification does not depend on a developer's local PostgreSQL password.

## Frontend

- `VITE_API_URL` points to the correct backend origin.
- Client-side routing fallback is configured for the static host.
- Login, registration, dashboard routing, tickets, chat, document upload, and lead analytics are tested manually.
- Empty states and loading states are checked with a fresh database.

## Data And Security

- No `.env` files are committed.
- No local database dumps, vector stores, or generated artifacts are committed.
- Demo data does not contain real customer information.
- Secrets are stored in the hosting provider's environment settings.
- Production CORS does not allow localhost.
- If using ChromaDB on Render, a persistent disk is attached and `CHROMA_DB_DIR` points under its mount path.

## Recruiter / Client Demo

- Add 4 to 6 screenshots in `docs/screenshots/`.
- Prepare one demo PDF for document-grounded chat.
- Prepare one customer account, one support account, and one admin account.
- Prepare a short demo script:
  1. Register/login.
  2. Create a ticket.
  3. Upload a support PDF.
  4. Ask the AI assistant a question answered by the PDF.
  5. Show citations.
  6. Show support/admin dashboard views.
  7. Show lead analytics.

## Known Production Tradeoffs

- Ollama is excellent for a local/private demo but needs a reachable host for cloud deployment. Use the OpenAI-compatible provider path when you want production AI without hosting Ollama.
- ChromaDB local persistence is simple for an MVP; the Render blueprint attaches a single-instance persistent disk. Managed vector storage is better for multi-tenant production scale.
- The app is production-minded, but a real paid SaaS would still need billing, organization workspaces, audit logs, stronger admin controls, rate limiting, and observability.
