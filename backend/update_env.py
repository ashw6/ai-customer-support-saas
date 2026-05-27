#!/usr/bin/env python3
"""
Script to update backend/.env with production-ready values.
Run this from the backend directory: python update_env.py
"""

import os
import shutil
from pathlib import Path

def update_env_file():
    """Update .env file with new secure values."""
    
    # New secure JWT_SECRET
    new_jwt_secret = "5lzo_lvwmYj9iuv5reR6Bq0v0jbM3CtYlHBe6kHzPI0"
    
    # Path to .env file
    env_path = Path(__file__).parent / ".env"
    env_backup_path = Path(__file__).parent / ".env.backup"
    
    # Backup existing .env
    if env_path.exists():
        shutil.copy(env_path, env_backup_path)
        print(f"✅ Backed up existing .env to .env.backup")
    
    # New production-ready .env content
    new_env_content = f"""# --- Core ---
ENVIRONMENT=production

# PostgreSQL - Keep your existing Neon database
DATABASE_URL=postgresql://neondb_owner:npg_Ieujt7iSU4gq@ep-wild-math-aqqut4sm.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require

# NEW SECURE JWT SECRET (rotated for production security)
JWT_SECRET={new_jwt_secret}

# JWT optional tuning
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# REPLACE WITH YOUR ACTUAL FRONTEND URL
CORS_ORIGINS=https://your-app.vercel.app

# REPLACE WITH YOUR ACTUAL FRONTEND URL
FRONTEND_URL=https://your-app.vercel.app

# Logging
LOG_LEVEL=INFO
SKIP_HEALTH_ACCESS_LOG=true

# --- AI chat / embeddings ---
AI_PROVIDER=ollama

# REPLACE WITH YOUR HOSTED OLLAMA ENDPOINT
# For local development, use: http://localhost:11434/api/generate
# For production, use your hosted Ollama URL
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
# Get your API key from: https://resend.com/api-keys
RESEND_API_KEY=your_resend_api_key_here
RESEND_FROM_EMAIL="AI Support <onboarding@yourdomain.com>"
RESEND_EMAILS_URL=https://api.resend.com/emails
RESEND_TIMEOUT_SECONDS=15

# Gmail SMTP fallback (optional, only used if RESEND_API_KEY is not set)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM_EMAIL="AI Support <you@gmail.com>"
SMTP_TIMEOUT_SECONDS=15

PASSWORD_RESET_EXPIRE_MINUTES=15
"""
    
    # Write new .env file
    with open(env_path, 'w') as f:
        f.write(new_env_content)
    
    print(f"✅ Updated .env with production-ready configuration")
    print(f"✅ New JWT_SECRET: {new_jwt_secret}")
    print(f"\n⚠️  MANUAL STEPS REQUIRED:")
    print(f"1. Update CORS_ORIGINS to your frontend URL")
    print(f"2. Update FRONTEND_URL to your frontend URL")
    print(f"3. Update OLLAMA_* URLs to your hosted Ollama endpoint")
    print(f"4. Update RESEND_API_KEY with your actual Resend API key")
    print(f"5. For local development, set ENVIRONMENT=development")
    print(f"6. For local development, use localhost Ollama URLs")
    print(f"\n📖 See PRODUCTION_SETUP_GUIDE.md for detailed instructions")

if __name__ == "__main__":
    update_env_file()
