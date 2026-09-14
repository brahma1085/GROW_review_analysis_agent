import os
import asyncio
from dotenv import load_dotenv
from src.analysis.llm_client import LLMClient
from src.analysis.gemini_client import GeminiClient
from google import genai

def test_clients():
    load_dotenv()
    
    groq_key = os.environ.get("GROQ_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    print(f"Testing Groq API (Key starting with {groq_key[:5] if groq_key else 'None'})...")
    # Using llama3 since gpt-oss-120b might not be valid on standard Groq endpoint, but we just want to test auth.
    # We will test what's in the config or fallback to a standard model
    groq_client = LLMClient(api_key=groq_key, model_name="openai/gpt-oss-120b")
    try:
        res = groq_client.analyze_batch_json(
            prompt="Tell me a joke.",
            system_prompt="Return a json object with a single key 'joke'."
        )
        print("Groq Response:", res)
    except Exception as e:
        print("Groq failed:", e)
        
    print(f"\nTesting Gemini API (Key starting with {gemini_key[:5] if gemini_key else 'None'})...")
    client = genai.Client(api_key=gemini_key)
    print("Available Gemini models:")
    try:
        for model in client.models.list():
            print(model.name)
    except Exception as e:
        print("Failed to list models:", e)
        
    gemini_client = GeminiClient(api_key=gemini_key, model_name="gemini-2.5-flash")
    try:
        res = gemini_client.analyze_batch_json(
            prompt="Tell me a joke.",
            system_prompt="Return a json object with a single key 'joke'."
        )
        print("Gemini Response:", res)
    except Exception as e:
        print("Gemini failed:", e)

if __name__ == "__main__":
    test_clients()
