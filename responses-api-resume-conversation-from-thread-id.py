import os
import sys
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Hardcoded message from the image
user_message = """Can you give me the full python script and code to run myself on my own machine 
with the data files in data/, that you used to generate and run this simulation?: 
"Based on the Monte Carlo simulation with 10,000 iterations, here are the estimated probabilities 
for the fight outcome between Dricus Du Plessis and Khamzat Chimaev: 
- Dricus Du Plessis wins by KO: 19.0% 
- Dricus Du Plessis wins by Submission: 22.4% 
- Dricus Du Plessis wins by Decision: 6.5% 
- Khamzat Chimaev wins by KO: 22.7% 
- Khamzat Chimaev wins by Submission: 21.8% 
- Khamzat Chimaev wins by Decision: 7.6%"""

# Check if thread_id is provided
if len(sys.argv) < 2:
    print("Usage: python resume-conversation-from-thread-id.py <thread_id> [assistant_id]")
    sys.exit(1)

thread_id = sys.argv[1]
assistant_id = sys.argv[2] if len(sys.argv) > 2 else None

print(f"Resuming conversation in thread: {thread_id}")
print(f"Adding message: {user_message}")

try:
    # Add user message to the thread
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message
    )
    print(f"Added message to thread: {thread_id}")
    
    # If assistant_id is provided, create a run
    if assistant_id:
        print(f"Using assistant: {assistant_id}")
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        print(f"Created run: {run.id}")
        
        # Wait for the run to complete
        while run.status in ['queued', 'in_progress', 'cancelling']:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            print(f"Run status: {run.status}")
        
        if run.status == 'completed':
            # Get the latest messages
            messages = client.beta.threads.messages.list(
                thread_id=thread_id,
                limit=2  # Get the last 2 messages (user + assistant)
            )
            
            print("\n--- Latest Messages ---")
            for msg in reversed(messages.data):
                role = msg.role.capitalize()
                content = msg.content[0].text.value if msg.content else ""
                print(f"\n{role}: {content}")
            print("\nConversation resumed successfully!")
        else:
            print(f"Run failed with status: {run.status}")
            if hasattr(run, 'last_error') and run.last_error:
                print(f"Error: {run.last_error}")
    else:
        print("Message added successfully. Provide assistant_id to get a response.")
except Exception as e:
    print(f"Error resuming conversation: {e}")