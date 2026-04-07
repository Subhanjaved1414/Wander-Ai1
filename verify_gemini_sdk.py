import google.generativeai as genai
import os

key = "AIzaSyBdetisr42F7nFi4DiX6rndvwQ1yTidO0A"
genai.configure(api_key=key)

print(f"Testing Gemini SDK with key: {key[:5]}...")
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello")
    print("SUCCESS")
    print(response.text)
except Exception as e:
    print(f"FAILED: {e}")
