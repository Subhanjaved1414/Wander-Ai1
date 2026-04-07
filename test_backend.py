import requests
import time

print("Testing Backend Chat Endpoint...")
url = "http://127.0.0.1:5000/chat/"
data = {"message": "Hello from test script"}

try:
    # Retry loop to wait for server start
    for i in range(5):
        try:
            r = requests.post(url, json=data, timeout=30)
            if r.status_code == 200:
                print("SUCCESS: Backend responded")
                print("Reply:", r.json().get("reply", "No reply field"))
                exit(0)
            else:
                print(f"FAILED: Status {r.status_code}")
                print(r.text)
                exit(1)
        except requests.exceptions.ConnectionError:
            print("Server not ready, retrying...")
            time.sleep(2)
    print("FAILED: Could not connect to server after retries")
    exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)
