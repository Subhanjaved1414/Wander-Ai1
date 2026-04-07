import requests
import json

key = "AIzaSyBdetisr42F7nFi4DiX6rndvwQ1yTidO0A"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"

with open("models_list.txt", "w") as f:
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            models = r.json().get('models', [])
            found = False
            for m in models:
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    f.write(f"{m['name']}\n")
                    found = True
            if not found:
                 f.write("No generateContent models found.\n")
        else:
            f.write(f"Failed: {r.text}")
    except Exception as e:
        f.write(f"Error: {e}")
