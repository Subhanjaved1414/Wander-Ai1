import google.generativeai as genai
import sys

print(f"Python: {sys.executable}")
try:
    print(f"Propagated keys: {dir(genai)}")
    if hasattr(genai, 'GenerativeModel'):
        print("SUCCESS: GenerativeModel class FOUND")
    else:
        print("FAILURE: GenerativeModel class NOT FOUND in genai module")
except Exception as e:
    print(f"Error inspecting genai: {e}")
