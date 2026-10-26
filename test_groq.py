
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

if not api_key:
    raise RuntimeError("GROQ_API_KEY is missing from .env")

client = Groq(api_key=api_key, timeout=30, max_retries=1)

try:
    print(f"Testing model: {model}")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: FACTINDIC API WORKS"
            }
        ],
        max_completion_tokens=50
    )

    print("SUCCESS:", response.choices[0].message.content)

except Exception as e:
    print(f"{type(e).__name__}: {e}")

finally:
    client.close()
