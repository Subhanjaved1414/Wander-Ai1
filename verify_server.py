import requests
import json

BASE_URL = "http://localhost:5000"

def test_home():
    print("Testing Home Page...")
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✅ Home Page is reachable.")
        else:
            print(f"❌ Home Page returned {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to reach Home Page: {e}")

def test_chatbot_page():
    print("\nTesting Chatbot Page...")
    try:
        response = requests.get(f"{BASE_URL}/chatbot.html")
        if response.status_code == 200:
            print("✅ Chatbot Page is reachable.")
        else:
            print(f"❌ Chatbot Page returned {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to reach Chatbot Page: {e}")

def test_chat_api():
    print("\nTesting Chat API...")
    url = f"{BASE_URL}/chat"
    payload = {"message": "Hello, this is a verify test."}
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "reply" in data:
                print(f"✅ Chat API responded: {data['reply'][:50]}...")
            else:
                print(f"❌ Chat API response missing 'reply': {data}")
        else:
            print(f"❌ Chat API returned {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Failed to reach Chat API: {e}")

if __name__ == "__main__":
    test_home()
    test_chatbot_page()
    test_chat_api()
