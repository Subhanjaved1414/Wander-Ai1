import requests
import json

key = "sk-739f40cb4da84e788d966f776b11ac0d"
url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {key}",
    "HTTP-Referer": "http://localhost:5000",
    "X-Title": "WanderAI",
    "Content-Type": "application/json"
}

models_to_test = [
    "provider-2/gpt-oss-120b",
    "gpt-oss-120b",
    "openai/gpt-oss-120b",
    "openai/gpt-4o-mini", # Fallback test
]

print("Testing OpenRouter Chat API with various models...")

for model in models_to_test:
    print(f"\n--- Testing Model: {model} ---")
    data = {
        "model": model,
        "messages": [{"role": "user", "content": "Hello"}]
    }
    try:
        r = requests.post(url, headers=headers, json=data, timeout=10)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            print(f"SUCCESS! Valid Model ID: {model}")
            print(r.text[:100])
            break
        else:
            print(f"Failed: {r.text}")
    except Exception as e:
        print(f"Error: {e}")
