"""
api/index.py - Vercel Serverless Function (ASGI)

Exports the FastAPI app directly for Vercel. No extra root_path needed because
Vercel maps /api/* to this function and passes the remaining path (e.g., /health).
"""

import sys
from pathlib import Path

# Ensure project root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the FastAPI app
from main import app

# Export for Vercel Python runtime
handler = app
