import requests

key = "sk-739f40cb4da84e788d966f776b11ac0d"
url = "https://openrouter.ai/api/v1/models"

print(f"Testing OpenRouter with key: {key[:5]}...")
try:
    r = requests.get(url, headers={"Authorization": f"Bearer {key}"}, timeout=10)
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        print("SUCCESS: Key is valid for OpenRouter.")
        # Check if model exists
        models = r.json().get("data", [])
        found = False
        for m in models:
            if "gpt-oss-120b" in m["id"] or "provider-2" in m["id"]:
                print(f"FOUND MODEL: {m['id']}")
                found = True
        if not found:
            print("Model 'gpt-oss-120b' NOT found in OpenRouter list.")
    else:
        print(f"Failed: {r.text}")
except Exception as e:
    print(f"Error: {e}")
