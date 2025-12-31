#!/usr/bin/env python3
"""
list_models.py - List available Gemini models

Run this to see which models are available for your API key.
Make sure GOOGLE_API_KEY is set in your environment.
"""

import os
import google.generativeai as genai

def list_available_models():
    """List all available Gemini models and their supported methods."""
    
    # Get API key from environment
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print('❌ Error: GOOGLE_API_KEY environment variable not set')
        print('Get a free key at: https://makersuite.google.com/app/apikey')
        return
    
    # Configure the API
    genai.configure(api_key=api_key)
    
    print('=' * 70)
    print('Available Gemini Models')
    print('=' * 70)
    print()
    
    # List all models
    try:
        models = list(genai.list_models())
        
        if not models:
            print('❌ No models found. Check your API key.')
            return
        
        print(f'📊 Total models found: {len(models)}')
        print()
        
        # Show ALL models first
        print('All available models:')
        print('-' * 70)
        for model in models:
            print(f'📦 {model.name}')
            print(f'   Display: {model.display_name}')
            print(f'   Methods: {model.supported_generation_methods}')
            print()
        
        # Filter for models that support generateContent
        content_models = [m for m in models if 'generateContent' in m.supported_generation_methods]
        
        print('=' * 70)
        print(f'✅ Models supporting generateContent: {len(content_models)}')
        print('=' * 70)
        
        if content_models:
            for model in content_models:
                print(f'📦 Model Name: {model.name}')
                print(f'   Display Name: {model.display_name}')
                print(f'   Description: {model.description}')
                print()
        
        print('=' * 70)
        print('Recommended model names to try:')
        print('  - gemini-1.5-flash')
        print('  - gemini-1.5-pro')
        print('  - gemini-pro')
        print('=' * 70)
        
    except Exception as e:
        print(f'❌ Error listing models: {e}')
        print('Make sure your API key is valid and has access to Gemini.')


if __name__ == '__main__':
    list_available_models()
