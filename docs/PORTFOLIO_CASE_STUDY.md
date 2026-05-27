# Portfolio Case Study

## Project Title

AI Customer Support & Sales Agent

## One-Line Summary

Built a full-stack AI support SaaS MVP with role-based dashboards, ticket management, PDF-grounded chat, lead capture, email automation, and production validation.

## Problem

Small teams often answer the same support questions repeatedly while leads and support requests get split across chat, email, documents, and spreadsheets. This project centralizes customer support workflows and uses AI retrieval to answer from company documents.

## Solution

The app gives customers a support portal, gives support teams ticket workflows, and gives admins analytics over documents, leads, and support activity. Staff/admin uploaded PDFs are parsed, embedded, stored in ChromaDB, and used by the chat assistant to produce grounded answers with citations.

## Key Features To Show

- Authentication and role-based routing
- Customer ticket creation and ticket detail pages
- Support/admin dashboards with filters and analytics
- AI chat with conversation history
- Staff/admin PDF upload and RAG citations
- Lead capture from chat activity
- Password reset and optional email workflows
- Production configuration checks and structured API errors

## Resume Bullets

- Built a full-stack AI customer support SaaS using React, TypeScript, FastAPI, PostgreSQL, ChromaDB, and Ollama.
- Implemented JWT authentication, role-based access control, ticket workflows, document upload, RAG chat, and lead analytics.
- Added Alembic migrations, request tracing, centralized exception handling, production environment validation, and frontend/backend tests.
- Designed recruiter-ready documentation with local setup, API overview, verification commands, and production-readiness notes.

## Interview Talking Points

- Why RAG was used instead of relying on a generic chatbot.
- How staff/admin uploaded PDFs become chunks, embeddings, vector records, and cited answers.
- How role-based access separates customer, support, and admin workflows.
- How the backend validates production settings to prevent insecure deployment.
- What you would improve for a paid multi-tenant SaaS: organizations, billing, rate limits, audit logs, managed vector DB, hosted LLM, and monitoring.

## Suggested Demo Script

1. Start with the customer view and create a support ticket.
2. Switch to support/admin view and show ticket visibility.
3. Upload a PDF into the document system as a support/admin user.
4. Ask the chat assistant a question that requires the PDF.
5. Point out the source citations.
6. Show lead capture and analytics.
7. End with the test/build commands and production checklist.

## GitHub README Additions To Add Later

- Live demo URL
- Demo video URL
- Screenshots from the actual app
- Demo credentials for customer, support, and admin users
- Architecture diagram image if you want stronger visual polish
