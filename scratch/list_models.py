import os
from google import genai

def load_env():
    env_vars = {}
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    env_vars[key.strip()] = val.strip()
    return env_vars

def main():
    env = load_env()
    api_key = env.get("GEMINI_API_KEY", "")
    if not api_key:
        print("No GEMINI_API_KEY found in .env!")
        return

    try:
        client = genai.Client(api_key=api_key)
        print("Listing available models via Google GenAI modern SDK:")
        for model in client.models.list():
            print(f"- {model.name} (Supported actions: {model.supported_actions})")
    except Exception as e:
        print(f"Modern GenAI SDK list failed: {e}")
        try:
            import google.generativeai as genai_legacy
            genai_legacy.configure(api_key=api_key)
            print("\nListing available models via Legacy GenerativeAI SDK:")
            for m in genai_legacy.list_models():
                print(f"- {m.name}")
        except Exception as e2:
            print(f"Legacy SDK list failed: {e2}")

if __name__ == '__main__':
    main()
