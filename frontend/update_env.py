#!/usr/bin/env python3
"""
Script to update frontend/.env.local with production-ready values.
Run this from the frontend directory: python update_env.py
"""

import os
import shutil
from pathlib import Path

def update_env_file():
    """Update .env.local file with new values."""
    
    # Path to .env.local file
    env_path = Path(__file__).parent / ".env.local"
    env_backup_path = Path(__file__).parent / ".env.local.backup"
    
    # Backup existing .env.local
    if env_path.exists():
        shutil.copy(env_path, env_backup_path)
        print(f"✅ Backed up existing .env.local to .env.local.backup")
    
    # New production-ready .env.local content
    new_env_content = """# Public API base (no trailing slash)
# For local development: http://127.0.0.1:8000
# For production: https://ai-customer-support-saas-ann0.onrender.com
VITE_API_URL=https://ai-customer-support-saas-ann0.onrender.com

# Axios timeout (milliseconds) - general API calls
VITE_API_TIMEOUT_MS=90000

# Chat /send can wait on an external AI provider (milliseconds)
VITE_CHAT_TIMEOUT_MS=180000
"""
    
    # Write new .env.local file
    with open(env_path, 'w') as f:
        f.write(new_env_content)
    
    print(f"✅ Updated .env.local with configuration")
    print(f"\n⚠️  MANUAL STEPS REQUIRED:")
    print(f"1. Production backend: VITE_API_URL=https://ai-customer-support-saas-ann0.onrender.com")
    print(f"2. For local development: Change VITE_API_URL=http://127.0.0.1:8000")

if __name__ == "__main__":
    update_env_file()
