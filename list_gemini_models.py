#!/usr/bin/env python3
"""
List all available Gemini models to find the correct embedding model name.
"""

import os
from google import genai

def list_all_models():
    """List all available models from Gemini API."""
    
    # Get API key from environment
    api_key = os.environ.get('GEMINI_API_KEY')    
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not found in environment!")
        print("\nSet it with:")
        print("  export GEMINI_API_KEY='your-key-here'  (Linux/Mac)")
        print("  set GEMINI_API_KEY=your-key-here       (Windows CMD)")
        print("  $env:GEMINI_API_KEY='your-key-here'    (Windows PowerShell)")
        return
    
    print("=" * 70)
    print("🔍 LISTING ALL AVAILABLE GEMINI MODELS")
    print("=" * 70)
    print()
    
    try:
        # Initialize client
        client = genai.Client(api_key=api_key)
        print("✅ Connected to Gemini API")
        print()
        
        # Get all models
        models = client.models.list()
        
        # Separate by type
        embedding_models = []
        generation_models = []
        other_models = []
        
        for model in models:
            name = model.name
            
            if 'embed' in name.lower():
                embedding_models.append(model)
            elif 'gemini' in name.lower() or 'flash' in name.lower():
                generation_models.append(model)
            else:
                other_models.append(model)
        
        # Display EMBEDDING models (most important)
        print("🎯 EMBEDDING MODELS (for RAG system):")
        print("-" * 70)
        if embedding_models:
            for model in embedding_models:
                print(f"  ✅ {model.name}")
                if hasattr(model, 'supported_generation_methods'):
                    print(f"     Methods: {model.supported_generation_methods}")
                if hasattr(model, 'description'):
                    print(f"     Description: {model.description}")
                print()
        else:
            print("  ❌ No embedding models found!")
        print()
        
        # Display GENERATION models
        print("💬 GENERATION MODELS (for text generation):")
        print("-" * 70)
        for model in generation_models[:5]:  # Show first 5
            print(f"  • {model.name}")
        if len(generation_models) > 5:
            print(f"  ... and {len(generation_models) - 5} more")
        print()
        
        # Display OTHER models
        if other_models:
            print("🔧 OTHER MODELS:")
            print("-" * 70)
            for model in other_models[:5]:
                print(f"  • {model.name}")
            if len(other_models) > 5:
                print(f"  ... and {len(other_models) - 5} more")
            print()
        
        # Summary
        print("=" * 70)
        print("📊 SUMMARY:")
        print(f"  Total models: {len(list(models))}")
        print(f"  Embedding models: {len(embedding_models)}")
        print(f"  Generation models: {len(generation_models)}")
        print(f"  Other models: {len(other_models)}")
        print("=" * 70)
        print()
        
        # Recommendation
        if embedding_models:
            print("💡 RECOMMENDED FOR RAG SYSTEM:")
            print(f"   Use: {embedding_models[0].name}")
            print()
            print("   In rag_query_system.py, use:")
            print(f"   model=\"{embedding_models[0].name}\"")
        else:
            print("⚠️  WARNING: No embedding models found!")
            print("   You may need to:")
            print("   1. Check your API key permissions")
            print("   2. Use the OLD google.generativeai API")
            print("   3. Contact Google AI support")
        
        print()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print()
        print("Possible issues:")
        print("  1. Invalid API key")
        print("  2. Network connection problem")
        print("  3. API version mismatch")
        print()
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    list_all_models()
