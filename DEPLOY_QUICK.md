# Quick Vercel Deployment Guide

## Prerequisites

You need Node.js installed to use Vercel CLI.

Check if you have it:
```bash
node --version
```

If not installed:
```bash
brew install node
```

## Option 1: Automated Script (Recommended)

Run the deployment script:

```bash
cd "/Users/saadelaboudi/Downloads/app howto/agentic_ai_cx_poc"
./deploy-vercel.sh
```

This will:
1. Install Vercel CLI if needed
2. Login to Vercel
3. Deploy your app to production

## Option 2: Manual Deployment

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login
```bash
vercel login
```

### Step 3: Deploy
```bash
cd "/Users/saadelaboudi/Downloads/app howto/agentic_ai_cx_poc"
vercel --prod
```

## Option 3: Deploy via GitHub (No CLI needed)

1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Click "New Project"
4. Import your repository: `SaadElAboudi/agentic-ai-cx-poc`
5. Click "Deploy"

Vercel will automatically:
- Detect it's a Python project
- Use `vercel.json` configuration
- Build and deploy both frontend and backend
- Give you a live URL

## After Deployment

Your app will be available at:
- **Production URL**: `https://agentic-ai-cx-poc.vercel.app`
- **Demo UI**: `https://agentic-ai-cx-poc.vercel.app/demo`
- **API Docs**: `https://agentic-ai-cx-poc.vercel.app/docs`

## Test Your Deployment

```bash
# Replace with your actual Vercel URL
curl https://agentic-ai-cx-poc.vercel.app/health

curl -X POST https://agentic-ai-cx-poc.vercel.app/agentic-cx \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"123","message":"I missed my appointment"}'
```

## Enable Agentic Mode

In Vercel Dashboard:
1. Go to your project
2. Settings → Environment Variables
3. Add: `AGENTIC_MODE` = `1`
4. Redeploy

Or via CLI:
```bash
vercel env add AGENTIC_MODE production
# Enter: 1
vercel --prod
```

## Redeploy After Changes

```bash
git add .
git commit -m "Your changes"
git push origin main
vercel --prod
```

Or if you connected via GitHub, Vercel auto-deploys on push.
