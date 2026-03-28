
import urllib.request
import urllib.error
import urllib.parse
import json
import config


def test_openrouter():
    models_to_try = [
        "deepseek/deepseek-r1", 
        "deepseek/deepseek-r1:free",
        "deepseek/deepseek-chat",
        "google/gemini-2.0-flash-001"
    ]
    
    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000"
    }

    for model in models_to_try:
        print(f"\nTrying model: {model}")
        data = {
            "model": model,
            "messages": [{"role": "user", "content": "Hello, are you alive?"}]
        }

        try:
            req = urllib.request.Request(config.OPENROUTER_URL, json.dumps(data).encode('utf-8'), headers)
            with urllib.request.urlopen(req) as response:
                print("Status Code:", response.getcode())
                print("Response:", response.read().decode())
                print(f"SUCCESS with {model}!")
                return
        except urllib.error.HTTPError as e:
            print(f"FAILED with {model}: {e.code}")
            try:
                print("Error Body:", e.read().decode())
            except:
                pass
        except Exception as e:
            print(f"Unexpected Error with {model}: {e}")


if __name__ == "__main__":
    test_openrouter()
