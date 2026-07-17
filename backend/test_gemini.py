from dotenv import load_dotenv
load_dotenv()
import os
from google import genai

key = os.environ.get("GEMINI_API_KEY")
print("Key loaded:", bool(key), "length:", len(key) if key else 0)

client = genai.Client(api_key=key)
response = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents="Say hello in one word."
)
print("Response:", response.text)