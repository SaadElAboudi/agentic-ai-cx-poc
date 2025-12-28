"""
api/index.py - Vercel Serverless Function Handler
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the FastAPI app
from main import app
from mangum import Mangum

# Wrap FastAPI app with Mangum for serverless
handler = Mangum(app, lifespan="off")
