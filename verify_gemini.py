import requests

key = "AIzaSyBdetisr42F7nFi4DiX6rndvwQ1yTidO0A"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"

data = {
    "contents": [{
        "parts": [{"text": "Hello"}]
    }]
}

print(f"Testing Gemini API with key: {key[:5]}...")
try:
    r = requests.post(url, json=data, timeout=10)
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        print("SUCCESS: Valid Gemini Key")
        print(r.text[:200])
    else:
        print(f"Failed: {r.text}")
except Exception as e:
    print(f"Error: {e}")
