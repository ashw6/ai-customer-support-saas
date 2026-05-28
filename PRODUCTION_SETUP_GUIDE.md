# Production Setup Guide

## Manual Steps Required

### 1. Update Backend .env File

Replace your `backend/.env` file with the following content (update the placeholders):

```bash
# --- Core ---
ENVIRONMENT=production

# PostgreSQL - Keep your existing Neon database
DATABASE_URL=postgresql://neondb_owner:npg_Ieujt7iSU4gq@ep-wild-math-aqqut4sm.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require

# NEW SECURE JWT SECRET (already generated for you)
JWT_SECRET=5lzo_lvwmYj9iuv5reR6Bq0v0jbM3CtYlHBe6kHzPI0

# JWT optional tuning
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Public frontend URL
CORS_ORIGINS=https://ai-customer-support-saas-rho.vercel.app

# Public frontend URL
FRONTEND_URL=https://ai-customer-support-saas-rho.vercel.app

# Logging
LOG_LEVEL=INFO
SKIP_HEALTH_ACCESS_LOG=true

# --- AI chat / embeddings ---
AI_PROVIDER=ollama

# REPLACE WITH YOUR HOSTED OLLAMA ENDPOINT
OLLAMA_GENERATE_URL=https://your-ollama-host.com/api/generate
OLLAMA_CHAT_URL=https://your-ollama-host.com/api/chat
OLLAMA_EMBEDDINGS_URL=https://your-ollama-host.com/api/embeddings
OLLAMA_CHAT_MODEL=mistral
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_TIMEOUT_SECONDS=120
OLLAMA_HISTORY_LIMIT=12
OLLAMA_NUM_PREDICT=120
RAG_MAX_CONTEXT_DISTANCE=0.60
OLLAMA_USE_CHAT_API=true
AI_CHAT_FALLBACK_ENABLED=false
AI_CHAT_FALLBACK_ONLY=false

# --- ChromaDB ---
CHROMA_DB_DIR=./chroma_db
CHROMA_COLLECTION=support_documents

# --- Email (Resend) ---
# REPLACE WITH YOUR RESEND API KEY
RESEND_API_KEY=your_resend_api_key_here
RESEND_FROM_EMAIL="AI Support <onboarding@yourdomain.com>"
RESEND_EMAILS_URL=https://api.resend.com/emails
RESEND_TIMEOUT_SECONDS=15

# Gmail SMTP fallback (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM_EMAIL="AI Support <you@gmail.com>"
SMTP_TIMEOUT_SECONDS=15

PASSWORD_RESET_EXPIRE_MINUTES=15
```

### 2. Get Resend API Key

1. Go to https://resend.com/api-keys
2. Sign up for a free account
3. Create an API key
4. Replace `your_resend_api_key_here` in your .env file with the actual key
5. Verify your sender domain in Resend dashboard

### 3. Set Up Hosted Ollama

**Option A: Use a cloud provider (Recommended)**
- RunPod: https://www.runpod.io/ - Deploy Ollama on GPU
- Modal: https://modal.com/ - Serverless Ollama
- Hugging Face Spaces: Deploy Ollama endpoint

**Option B: Self-hosted VPS**
- Get a VPS (DigitalOcean, AWS EC2, etc.)
- Install Ollama: https://ollama.com/download
- Expose port 11434 with SSL
- Update OLLAMA_* URLs in .env

**Option C: Use OpenAI instead (Simpler)**
If you don't want to host Ollama, switch to OpenAI:
```bash
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### 4. Update Frontend .env.local

Create or update `frontend/.env.local`:

```bash
# For local development
VITE_API_URL=http://127.0.0.1:8000

# For production
VITE_API_URL=https://ai-customer-support-saas-ann0.onrender.com

VITE_API_TIMEOUT_MS=90000
VITE_CHAT_TIMEOUT_MS=180000
```

### 5. Deploy Backend to Render

1. Push your code to GitHub
2. Go to https://render.com/
3. Create new Web Service
4. Connect your GitHub repository
4. Set environment variables (copy from your .env file)
5. Set build command: `pip install -r requirements.txt`
6. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. Add pre-deploy command: `python -m alembic upgrade head`
8. Deploy

### 6. Deploy Frontend to Vercel

1. Push your code to GitHub
2. Go to https://vercel.com/
3. Import your repository
4. Set environment variable: `VITE_API_URL=https://ai-customer-support-saas-ann0.onrender.com`
5. Deploy

### 7. Update URLs in Backend .env

After deployment:
1. Render backend URL: `https://ai-customer-support-saas-ann0.onrender.com`
2. Vercel frontend URL: `https://ai-customer-support-saas-rho.vercel.app`
3. Update backend .env:
   - `CORS_ORIGINS=https://ai-customer-support-saas-rho.vercel.app`
   - `FRONTEND_URL=https://ai-customer-support-saas-rho.vercel.app`
4. Update frontend .env.local:
   - `VITE_API_URL=https://ai-customer-support-saas-ann0.onrender.com`
5. Redeploy both services

## Quick Start for Local Development

If you want to test locally before deploying:

```bash
# Backend
cd backend
# Use the .env.production file as template
cp .env.production .env
# Update OLLAMA URLs to localhost for local testing
# Set ENVIRONMENT=development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## Security Notes

- ✅ JWT_SECRET has been rotated to a new secure value
- ✅ Database credentials are in .env (gitignored)
- ⚠️ Never commit .env files to git
- ⚠️ Never share API keys publicly
- ⚠️ Use environment variables in production, never hardcode secrets

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend connects to backend
- [ ] User registration works
- [ ] User login works
- [ ] Password reset email sends
- [ ] Document upload works
- [ ] AI chat responds (if Ollama/OpenAI configured)
- [ ] Lead capture works
- [ ] Admin dashboard loads
- [ ] All role-based access works

## Support

If you encounter issues:
1. Check backend logs: `Render Dashboard > Logs`
2. Check frontend console: Browser DevTools
3. Verify environment variables are set correctly
4. Ensure CORS origins match your frontend URL
5. Verify database connection string is correct
