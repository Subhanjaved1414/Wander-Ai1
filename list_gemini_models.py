import google.generativeai as genai
import os

key = "AIzaSyBdetisr42F7nFi4DiX6rndvwQ1yTidO0A"
genai.configure(api_key=key)

print(f"Listing models for key: {key[:5]}...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"FOUND: {m.name}")
except Exception as e:
    print(f"FAILED: {e}")
