# Agentic AI CX - Vercel Deployment Guide

## Prerequisites

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

## Deploy to Vercel

### Quick Deploy

From the project directory:

```bash
cd "/Users/saadelaboudi/Downloads/app howto/agentic_ai_cx_poc"
vercel
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? Select your account
- Link to existing project? **N**
- What's your project's name? `agentic-ai-cx-poc`
- In which directory is your code located? `./`
- Want to override the settings? **N**

### Deploy with Custom Settings

```bash
vercel --prod
```

## Environment Variables

Set in Vercel Dashboard or via CLI:

```bash
vercel env add AGENTIC_MODE
# Enter value: 0 (or 1 to enable agentic planner mode)
```

## Access Your Deployment

After deployment completes, you'll get URLs:

- **Preview**: `https://agentic-ai-cx-poc-xxxxx.vercel.app`
- **Production**: `https://agentic-ai-cx-poc.vercel.app`

### Endpoints

- Frontend (Demo UI): `https://your-app.vercel.app/demo`
- API Health Check: `https://your-app.vercel.app/health`
- API Docs: `https://your-app.vercel.app/docs`
- Main API: `https://your-app.vercel.app/agentic-cx`

## Test Your Deployment

```bash
# Health check
curl https://your-app.vercel.app/health

# Test API
curl -X POST https://your-app.vercel.app/agentic-cx \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"123","message":"I missed my appointment yesterday, can I rebook?"}'
```

## Configuration Files

- `vercel.json`: Vercel deployment configuration
- `requirements.txt`: Python dependencies
- `main.py`: Updated with Vercel handler export

## Redeploy

To redeploy after changes:

```bash
git add .
git commit -m "Update for Vercel deployment"
git push origin main
vercel --prod
```

## Troubleshooting

### Build Fails

Check Python version (Vercel uses 3.9 by default):
- Add `runtime.txt` if you need specific Python version

### CORS Issues

Already configured in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Data Files Not Found

Ensure `data/` directory is committed to git and deployed.

## Custom Domain

In Vercel Dashboard:
1. Go to your project
2. Settings → Domains
3. Add your custom domain
4. Update DNS records as instructed

## Production Settings

For production, update `vercel.json`:

```json
{
  "env": {
    "AGENTIC_MODE": "1",
    "LOG_LEVEL": "warning"
  }
}
```

Then redeploy with `vercel --prod`.
