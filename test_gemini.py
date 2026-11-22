
import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing. Add it to the .env file.")

# Initialize Gemini
client = genai.Client(api_key=api_key)

# Test Gemini connection
response = client.models.generate_content(
    model="gemini-flash-lite-latest",
    contents="Explain supply chain management briefly."
)

print("Gemini API connected successfully!")
print(response.text)

