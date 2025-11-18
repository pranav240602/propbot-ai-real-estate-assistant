import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

if api_key and api_key.startswith('sk-'):
    print("✅ OpenAI API key loaded successfully!")
    print(f"✅ Key starts with: {api_key[:20]}...")
else:
    print("❌ API key not found or invalid")
