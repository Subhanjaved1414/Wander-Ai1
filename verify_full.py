import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_home():
    print("Testing Home Page...")
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Home Page is reachable.")
        else:
            print(f"❌ Home Page returned {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to reach Home Page: {e}")

def test_chatbot():
    print("\nTesting Chatbot API...")
    url = f"{BASE_URL}/chat"
    payload = {"message": "Hello"}
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"✅ Chatbot responded: {response.json().get('reply', '')[:30]}...")
        else:
            print(f"❌ Chatbot failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Chatbot API error: {e}")

def test_recommender():
    print("\nTesting Recommender API (This triggers lazy load)...")
    url = f"{BASE_URL}/recommend" # Corrected endpoint based on app.py
    # app.register_blueprint(recommender_bp, url_prefix="/recommend") -> route is "/" inside blueprint
    
    payload = {
        "budget": 2000,
        "season": "Summer",
        "type": "City"
    }
    
    start_time = time.time()
    try:
        # First request might be slow due to loading
        print("⏳ Sending first request (expect delay)...")
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                 print(f"✅ Recommendation success ({duration:.2f}s). Got {len(data)} items.")
                 print(f"   Top: {data[0].get('Destination', 'Unknown')}")
            else:
                 print(f"⚠️ Recommendation returned empty or invalid format: {data}")
        else:
            print(f"❌ Recommender failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Recommender API error: {e}")

if __name__ == "__main__":
    test_home()
    test_chatbot()
    test_recommender()
