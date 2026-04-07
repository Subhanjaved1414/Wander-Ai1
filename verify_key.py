import requests
import sys

key = "sk-739f40cb4da84e788d966f776b11ac0d"

def test_openai():
    print("Testing OpenAI...")
    try:
        r = requests.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {key}"}, timeout=10)
        if r.status_code == 200:
            print("SUCCESS: Valid OpenAI Key")
            return "openai"
        print(f"OpenAI Failed: {r.status_code} {r.text}")
    except Exception as e:
        print(f"OpenAI Error: {e}")
    return None

def test_deepseek():
    print("Testing DeepSeek...")
    try:
        r = requests.get("https://api.deepseek.com/models", headers={"Authorization": f"Bearer {key}"}, timeout=10)
        if r.status_code == 200:
            print("SUCCESS: Valid DeepSeek Key")
            return "deepseek"
        print(f"DeepSeek Failed: {r.status_code} {r.text}")
    except Exception as e:
        print(f"DeepSeek Error: {e}")
    return None

if __name__ == "__main__":
    if test_openai():
        sys.exit(0)
    if test_deepseek():
        sys.exit(0)
    print("FAILURE: Key invalid for both OpenAI and DeepSeek")
