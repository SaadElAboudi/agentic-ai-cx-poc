#!/bin/bash

# Vercel Deployment Script for Agentic AI CX PoC

echo "================================================"
echo "Vercel Deployment for Agentic AI CX PoC"
echo "================================================"
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found."
    echo ""
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "⚠️  npm not found. Please install Node.js first:"
        echo "   brew install node"
        echo ""
        echo "Then run this script again."
        exit 1
    fi
fi

echo "✅ Vercel CLI ready"
echo ""

# Login to Vercel
echo "🔐 Logging in to Vercel..."
vercel login

if [ $? -ne 0 ]; then
    echo "❌ Login failed. Please try again."
    exit 1
fi

echo ""
echo "🚀 Deploying to Vercel..."
echo ""

# Deploy to production
vercel --prod

echo ""
echo "================================================"
echo "✅ Deployment Complete!"
echo "================================================"
echo ""
echo "Your app is now live at the URL shown above."
echo ""
echo "📍 Endpoints:"
echo "   - Demo UI: https://your-app.vercel.app/demo"
echo "   - API Health: https://your-app.vercel.app/health"
echo "   - API Docs: https://your-app.vercel.app/docs"
echo "   - Main API: https://your-app.vercel.app/agentic-cx"
echo ""
echo "🔧 To enable agentic mode, set environment variable:"
echo "   vercel env add AGENTIC_MODE"
echo "   Enter value: 1"
echo ""
