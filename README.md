# AI Customer Support & Sales Agent

A production-minded full-stack SaaS MVP for AI-assisted customer support, document-grounded chat, ticket management, and lead capture.

This project is built as a portfolio and client-demo application: a React dashboard for customers, support agents, and admins backed by a FastAPI API, PostgreSQL persistence, ChromaDB vector search, and Ollama-powered RAG workflows.

## What It Solves

Businesses often have product FAQs, policy PDFs, support tickets, and sales leads spread across disconnected tools. This app brings the core workflow into one system:

- Customers can register, open tickets, and chat with an AI assistant.
- The assistant can answer from staff/admin uploaded documents and return source citations.
- Support teams can manage and filter tickets.
- Admins can view analytics, uploaded documents, and captured leads.
- Optional email automation supports welcome, password reset, and lead follow-up flows.

## Highlights

- JWT authentication with register, login, current-user, forgot-password, and reset-password flows
- Role-based access for customer, support agent, and admin workflows
- Ticket creation, listing, filtering, pagination, and detail pages
- AI chat with conversation history and document-grounded RAG citations
- Staff/admin PDF ingestion with ChromaDB-backed vector search
- Lead capture from chat intent and admin lead analytics
- Optional Resend/Gmail email delivery with graceful failure handling
- Alembic database migrations for PostgreSQL
- Structured logging, request IDs, centralized JSON error responses, and production config validation
- Tested frontend and backend paths with reproducible verification commands

## Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, React Router, Axios, Recharts |
| Backend | FastAPI, SQLAlchemy, Alembic, Pydantic, python-jose, passlib |
| Database | PostgreSQL, compatible with Supabase connection strings |
| AI / RAG | Ollama or OpenAI-compatible chat/embeddings, ChromaDB, pypdf |
| Email | Resend API or Gmail SMTP fallback |
| Testing | Vitest, React Testing Library, Pytest |
| Deployment files | Vercel config for frontend, Render blueprint for backend |

## Architecture

```text
Browser: React + Vite + Tailwind
  |
  | HTTPS / JSON through VITE_API_URL
  v
FastAPI backend
  |
  +-- PostgreSQL: users, tickets, conversations, documents, leads
  +-- ChromaDB: persisted vector index
  +-- AI provider: local/hosted Ollama or OpenAI-compatible API
  +-- Resend / SMTP: optional transactional email
```

The frontend talks to the backend over REST. The backend owns authentication, role checks, persistence, email orchestration, document ingestion, retrieval, and AI response generation.

## Repository Layout

```text
.
|-- backend/
|   |-- ai/                 # RAG, PDF parsing, embeddings, Ollama, ChromaDB
|   |-- alembic/            # Database migrations
|   |-- database/           # SQLAlchemy engine and sessions
|   |-- middleware/         # Request ID and HTTP logging
|   |-- models/             # ORM models
|   |-- routes/             # API routers
|   |-- schemas/            # Pydantic schemas
|   |-- services/           # Service integrations
|   |-- tests/              # Backend tests
|   |-- utils/              # Auth, email, dependencies, exception handling
|   |-- main.py             # FastAPI app setup
|   |-- settings.py         # Environment settings and production validation
|   |-- requirements.txt
|   `-- requirements-dev.txt
|-- frontend/
|   |-- src/
|   |-- package.json
|   |-- vercel.json
|   `-- vite.config.ts
|-- docs/
|   |-- PORTFOLIO_CASE_STUDY.md
|   |-- PRODUCTION_READINESS.md
|   |-- UPWORK_CLIENT_OFFER.md
|   `-- screenshots/
|-- render.yaml
|-- .env.example
|-- .gitignore
`-- README.md
```

## Local Setup

### Prerequisites

- Node.js 20+
- Python 3.12+ recommended
- PostgreSQL
- Ollama installed locally for chat and embeddings

### 1. Backend Environment

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
copy .env.example .env
```

Edit `backend/.env` and set at least:

```text
DATABASE_URL=postgresql://...
JWT_SECRET=replace-with-a-long-random-secret-min-32-chars
```

Run migrations:

```bash
alembic upgrade head
```

Create local demo logins:

```bash
python scripts/seed_demo_users.py
```

Demo accounts:

| Role | Email | Password |
| --- | --- | --- |
| Customer / client | `customer@example.com` | `Customer123` |
| Company owner | `owner@example.com` | `Owner12345` |
| Support agent | `support@example.com` | `Support123` |

Start the API:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```text
GET http://127.0.0.1:8000/health
```

### 2. AI Provider

For production AI without managing GPU hosting, use an OpenAI-compatible provider:

```text
AI_PROVIDER=openai
OPENAI_API_KEY=...
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

For local development, Ollama is still the default.

The default local setup expects:

```bash
ollama pull mistral
ollama pull nomic-embed-text
ollama serve
```

Make sure the `OLLAMA_GENERATE_URL` and `OLLAMA_EMBEDDINGS_URL` values in `backend/.env` match your Ollama host.

For local demos, `AI_CHAT_FALLBACK_ENABLED=true` lets chat return a basic support reply when Ollama is not running. Set `AI_CHAT_FALLBACK_ONLY=true` when you want instant demo replies without waiting for Ollama. For true RAG answers with uploaded-document citations, set `AI_CHAT_FALLBACK_ONLY=false`, keep Ollama running, and upload PDFs from the company-owner account.

### 3. Frontend Environment

```bash
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Set:

```text
VITE_API_URL=http://127.0.0.1:8000
```

Open the Vite URL, usually `http://localhost:5173`.

## Environment Variables

### Backend

| Variable | Purpose |
| --- | --- |
| `ENVIRONMENT` | `development` or `production`; production enables stricter startup checks |
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET` | JWT signing secret; use at least 32 random characters in production |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins |
| `FRONTEND_URL` | Used in password reset links |
| `AI_PROVIDER` | `ollama` or `openai` |
| `OLLAMA_GENERATE_URL` | Ollama generation endpoint |
| `OLLAMA_EMBEDDINGS_URL` | Ollama embeddings endpoint |
| `OLLAMA_CHAT_MODEL` | Chat model name |
| `OLLAMA_EMBEDDING_MODEL` | Embedding model name |
| `OPENAI_API_KEY` | Required when `AI_PROVIDER=openai` |
| `OPENAI_CHAT_MODEL` | OpenAI-compatible chat model |
| `OPENAI_EMBEDDING_MODEL` | OpenAI-compatible embedding model |
| `CHROMA_DB_DIR` | ChromaDB persistence directory |
| `CHROMA_COLLECTION` | ChromaDB collection name |
| `RESEND_API_KEY` | Optional Resend email API key |
| `RESEND_FROM_EMAIL` | Optional verified sender address |
| `SMTP_*` | Optional Gmail SMTP fallback settings |
| `LOG_LEVEL` | Application log level |
| `SKIP_HEALTH_ACCESS_LOG` | Reduces health-check log noise |

### Frontend

| Variable | Purpose |
| --- | --- |
| `VITE_API_URL` | Backend base URL with no trailing slash |
| `VITE_API_TIMEOUT_MS` | Axios timeout in milliseconds; use `90000` locally for Ollama |

## API Overview

Base URL: `http://127.0.0.1:8000` locally.

Authenticated routes expect:

```text
Authorization: Bearer <access_token>
```

| Area | Routes |
| --- | --- |
| Auth | `/auth/register`, `/auth/login`, `/auth/me`, `/auth/forgot-password`, `/auth/reset-password` |
| Tickets | `/tickets`, `/tickets/my`, `/tickets/{id}` |
| Chat | `/chat/send`, `/chat/history`, `/chat/conversation/{id}` |
| Documents | `/documents/*` |
| Leads | `/leads`, `/leads/analytics` |
| Role dashboards | `/api/admin/dashboard`, `/api/support/tickets`, role-gated examples |
| Health | `/health` |

Interactive API docs are available at `/docs` while the backend is running.

## Verification

Run these before sharing the project with recruiters or clients:

```bash
cd backend
.venv\Scripts\activate
python -m pytest tests
```

```bash
cd frontend
npm test
npm run build
```

Current verified status:

- Backend tests: 17 passing
- Frontend tests: 4 passing
- Frontend production build: passing

## Production Readiness Notes

Implemented safeguards:

- Production startup validation requires `DATABASE_URL`, `JWT_SECRET`, and explicit non-localhost CORS origins.
- CORS is configured from environment variables.
- Global exception handlers return consistent JSON errors.
- Responses expose `X-Request-ID` for debugging.
- Email delivery degrades gracefully when providers are not configured or fail.
- RAG/Ollama failures return clear API errors instead of crashing the process.
- Build and test commands are documented for repeatable handoff.

See [docs/PRODUCTION_READINESS.md](docs/PRODUCTION_READINESS.md) for the checklist.

## Portfolio Positioning

Use this as a case-study project, not just a code dump. Suggested headline:

> Built a full-stack AI support SaaS with role-based dashboards, ticket workflows, PDF-grounded chat, lead capture, email automation, and production validation.

See [docs/PORTFOLIO_CASE_STUDY.md](docs/PORTFOLIO_CASE_STUDY.md) for resume bullets, interview talking points, and a project narrative.

## Upwork Positioning

Suggested service title:

> I will build an AI customer support chatbot trained on your PDFs, FAQs, and support docs.

See [docs/UPWORK_CLIENT_OFFER.md](docs/UPWORK_CLIENT_OFFER.md) for a first-client offer, proposal template, package structure, and delivery checklist.

## Demo Data

This repository does not ship shared demo accounts. For a demo:

1. Run migrations.
2. Register a user through the UI or `/auth/register`.
3. Assign support/admin roles in the database as needed.
4. Upload one or more product/support PDFs as a support agent or admin.
5. Create example tickets and chat conversations.

## Scripts

| Location | Command | Purpose |
| --- | --- | --- |
| `frontend/` | `npm run dev` | Start Vite dev server |
| `frontend/` | `npm run typecheck` | Run TypeScript checks |
| `frontend/` | `npm run build` | Create production frontend build |
| `frontend/` | `npm test` | Run frontend tests |
| `backend/` | `uvicorn main:app --reload` | Start backend dev server |
| `backend/` | `python -m pytest tests` | Run backend tests |
| `backend/` | `alembic upgrade head` | Apply database migrations |

## Security Checklist Before Public Sharing

- Do not commit `.env`, `.env.local`, virtual environments, `node_modules`, `dist`, `chroma_db`, caches, or generated bytecode.
- Use a fresh random `JWT_SECRET` for every environment.
- Use HTTPS frontend origins in production `CORS_ORIGINS`.
- Rotate any keys that were ever exposed locally or in screenshots.
- Remove personal emails, local database credentials, and test secrets before publishing.

## License

Use and adapt for learning, portfolio, and client-demo purposes. Replace branding, domains, demo data, and secrets before any real production use.
