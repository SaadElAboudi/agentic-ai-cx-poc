# Agentic AI CX PoC - Deployment Guide

## Docker Deployment

### Quick Start with Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# The API will be available at http://localhost:8000
```

### Manual Docker Build

```bash
# Build the image
docker build -t agentic-cx-poc:latest .

# Run the container
docker run -p 8000:8000 agentic-cx-poc:latest

# With volume mount for data changes
docker run -p 8000:8000 -v $(pwd)/data:/app/data agentic-cx-poc:latest
```

## Local Development

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the server
python3 main.py

# In another terminal, run tests
python3 test_agent.py
```

## Environment Variables

```bash
# API Server
API_HOST=0.0.0.0
API_PORT=8000

# LLM Integration (Google Gemini - FREE)
GOOGLE_API_KEY=your_free_gemini_key_from_https://makersuite.google.com/app/apikey
LLM_MODEL=gemini-pro

# CX Platform Integration (future)
GENESYS_API_KEY=...
GENESYS_REGION=us-east-1
```

## Production Checklist

- [ ] Environment-based configuration (not hardcoded)
- [ ] Secrets management (AWS Secrets Manager, HashiCorp Vault)
- [ ] Database persistence (PostgreSQL)
- [ ] Real LLM integration (OpenAI, Anthropic)
- [ ] Real CX API integration (Genesys, Twilio)
- [ ] Authentication & authorization (OAuth2, API keys)
- [ ] Rate limiting & DDoS protection
- [ ] Comprehensive logging & monitoring
- [ ] Error tracking (Sentry, DataDog)
- [ ] Load testing & performance tuning
- [ ] Security scanning & penetration testing
- [ ] Deployment pipeline (CI/CD)
- [ ] Auto-scaling configuration
- [ ] Disaster recovery & backup strategy
