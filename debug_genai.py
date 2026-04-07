import google.generativeai as genai
import sys

print(f"Python: {sys.executable}")
try:
    print(f"Path: {genai.__file__}")
    print(f"Version (if any): {getattr(genai, '__version__', 'None')}")
except Exception as e:
    print(f"Error: {e}")
