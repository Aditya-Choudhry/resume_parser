import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

# OpenRouter API Configuration
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

# Function to test the API
def test_api():
    prompt = "What can you do?"
    try:
        completion = client.chat.completions.create(
            model="deepseek/deepseek-r1-distill-llama-70b:free",
            messages=[{"role": "user", "content": prompt}],
        )
        print("API Response:")
        print(completion.choices[0].message.content)
    except Exception as e:
        print(f"Failed to test API. Error: {e}")

# Run the test
if __name__ == "__main__":
    test_api()
