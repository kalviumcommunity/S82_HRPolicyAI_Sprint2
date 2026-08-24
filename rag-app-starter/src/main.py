import os
import sys

def main():
    print("Initializing HRPolicyAI Environment Health Check...")
    
    # 1. Verify Python environment
    print(f"Python Version: {sys.version}")
    
    # 2. Verify dependencies are installed
    try:
        import dotenv
        import openai
        import chromadb
        print("Successfully imported all required packages: python-dotenv, openai, chromadb.")
    except ImportError as e:
        print(f"\n[ERROR] Missing required library: {e}")
        print("Make sure you have activated the virtual environment and run 'pip install -r requirements.txt'")
        sys.exit(1)
        
    # 3. Load environment variables
    dotenv.load_dotenv()
    
    api_base_url = os.getenv("API_BASE_URL", "Not Set")
    chat_model = os.getenv("CHAT_MODEL", "Not Set")
    embedding_model = os.getenv("EMBEDDING_MODEL", "Not Set")
    
    # Check if API Key exists (do NOT print the actual key)
    api_key_present = "Configured" if os.getenv("OPENAI_API_KEY") else "Not Configured"
    
    print("\nEnvironment Configuration Status:")
    print(f"  API_BASE_URL:    {api_base_url}")
    print(f"  OPENAI_API_KEY:  {api_key_present}")
    print(f"  CHAT_MODEL:      {chat_model}")
    print(f"  EMBEDDING_MODEL: {embedding_model}")
    
    print("\nHRPolicyAI environment is ready.")

if __name__ == "__main__":
    main()
