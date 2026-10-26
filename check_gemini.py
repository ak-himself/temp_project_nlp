
import os
import json
import urllib.request
import urllib.parse
import urllib.error
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GEMINI_API_KEY")

if not key:
    print("ERROR: Python cannot find GEMINI_API_KEY in .env")
    raise SystemExit(1)

url = (
    "https://generativelanguage.googleapis.com/v1beta/models?"
    + urllib.parse.urlencode({"key": key})
)

request = urllib.request.Request(url)

try:
    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.loads(response.read())
        models = [
            model["name"]
            for model in data.get("models", [])
            if "generateContent" in model.get("supportedGenerationMethods", [])
        ]
        print("API key accepted.")
        print("Models available for text generation:")
        for model in models:
            print(model)

except urllib.error.HTTPError as e:
    print("HTTP error:", e.code)
    print(e.read().decode())

except Exception as e:
    print(type(e).__name__ + ":", e)
