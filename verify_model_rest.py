import requests
import json
import os
from dotenv import load_dotenv

load_dotenv("services/.env")
key = os.getenv("GEMINI_API_KEY")

models_to_test = ["gemini-pro"]

print(f"Testing models with key: {key[:5]}...")
headers = {"Content-Type": "application/json"}
payload = {"contents": [{"parts": [{"text": "Hello"}]}]}

for m in models_to_test:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={key}"
    print(f"\n--- Testing {m} ---")
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            print(f"SUCCESS! {m} works.")
        else:
            print(f"Failed: {r.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
