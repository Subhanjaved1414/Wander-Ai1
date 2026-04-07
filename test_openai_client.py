from openai import OpenAI
import os

key = "sk-739f40cb4da84e788d966f776b11ac0d"
print(f"Testing OpenAI Client with OpenRouter (Key: {key[:5]}...)")

client = OpenAI(
    api_key=key,
    base_url="https://openrouter.ai/api/v1"
)

try:
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "user", "content": "Hello"}
        ],
    )
    print("SUCCESS")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"FAILED: {e}")
