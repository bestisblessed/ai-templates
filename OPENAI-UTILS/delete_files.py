import json
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load the JSON file
with open('output.json', 'r') as f:
    data = json.load(f)

# Set your API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")  # Ensure this is set in your .env
headers = {"Authorization": f"Bearer {api_key}"}

# Loop through files and delete each one
for file in data['data']:
    file_id = file['id']
    url = f"https://api.openai.com/v1/files/{file_id}"
    response = requests.delete(url, headers=headers)
    print(f"Deleted {file_id}: {response.json()}")
