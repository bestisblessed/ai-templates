from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))  # Ensure this is set in your .env
# Initialize empty list for assistant IDs
assistant_ids = []

# Read assistant IDs from the file
with open('assistants.txt', 'r') as f:
    for line in f:
        if line.startswith('Assistant ID:'):
            # Extract the ID from the line
            assistant_id = line.split(': ')[1].strip()
            assistant_ids.append(assistant_id)

# Delete each assistant
for assistant_id in assistant_ids:
    try:
        response = client.beta.assistants.delete(assistant_id)
        print(f"Successfully deleted {assistant_id}")
    except Exception as e:
        print(f"Error deleting {assistant_id}: {str(e)}")

print(f"\nAttempted to delete {len(assistant_ids)} assistants")