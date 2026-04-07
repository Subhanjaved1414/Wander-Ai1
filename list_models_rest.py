import requests
import json

key = "AIzaSyBdetisr42F7nFi4DiX6rndvwQ1yTidO0A"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"

print(f"Listing models via REST for key: {key[:5]}...")
try:
    r = requests.get(url, timeout=10)
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        models = r.json().get('models', [])
        for m in models:
            if 'generateContent' in m.get('supportedGenerationMethods', []):
                print(f"FOUND: {m['name']}")
    else:
        print(f"Failed: {r.text}")
except Exception as e:
    print(f"Error: {e}")
