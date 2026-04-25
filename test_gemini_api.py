import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ No API key found in .env file!")
    exit(1)

print(f"✅ API Key loaded: {api_key[:10]}...{api_key[-4:]}")

# Configure Gemini
genai.configure(api_key=api_key)

# Test embedding
try:
    result = genai.embed_content(
        model="models/text-embedding-004",
        content="Test embedding",
        task_type="retrieval_document"
    )
    
    embedding = result['embedding']
    print(f"✅ Embedding generated: {len(embedding)} dimensions")
    print(f"✅ First 5 values: {embedding[:5]}")
    print("\n🎉 Gemini API is working!")
    
except Exception as e:
    print(f"❌ Error: {e}")