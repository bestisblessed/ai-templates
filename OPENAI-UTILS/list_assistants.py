from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize client with your API key from the environment variable
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))  # Ensure this is set in your .env

# List all assistants without limit
my_assistants = client.beta.assistants.list(
    order="desc",
    limit="99",
)

# Save results to a file
with open('assistants.txt', 'w') as f:
    for assistant in my_assistants.data:
        f.write(f"Assistant ID: {assistant.id}\n")
        f.write(f"Name: {assistant.name}\n")
        f.write(f"Model: {assistant.model}\n")
        f.write(f"Description: {assistant.description}\n")
        f.write("-" * 50 + "\n")
