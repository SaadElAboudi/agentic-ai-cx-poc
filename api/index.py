"""Test with direct ASGI app export"""
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/health")
def health():
    return {"status": "healthy"}

@app.get("/{path:path}")  
def root(path: str):
    return {"path": path, "works": True}
