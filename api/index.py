"""
api/index.py - Vercel Serverless Function (ASGI)

Expose the FastAPI application under the "/api" base path for Vercel.
"""

import sys
from pathlib import Path
from fastapi import FastAPI

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import base FastAPI app
from main import app as base_app

# Create proxy app with root_path "/api" and mount the base app at "/"
proxy_app = FastAPI(root_path="/api")
proxy_app.mount("/", base_app)

# Export ASGI app for Vercel Python runtime
app = proxy_app
