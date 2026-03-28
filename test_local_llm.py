
import urllib.request
import json
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

def test_local_llm():
    url = "http://localhost:11434/api/tags" # Standard Ollama endpoint
    print(f"Testing connectivity to: {url}")
    
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            if response.getcode() == 200:
                print("SUCCESS: Local LLM Service is Reachable!")
                data = json.load(response)
                print("Available Models:")
                for model in data.get('models', []):
                    print(f"- {model['name']}")
            else:
                print(f"WARNING: Server returned status {response.getcode()}")
    except Exception as e:
        print(f"ERROR: Could not connect to Local LLM.")
        print(f"Details: {e}")
        print("\nTROUBLESHOOTING:")
        print("1. Make sure Ollama (or your LLM server) is running.")
        print("2. Check if it's listening on port 11434.")
        print("3. If using WSL, check firewall/networking.")

if __name__ == "__main__":
    test_local_llm()
