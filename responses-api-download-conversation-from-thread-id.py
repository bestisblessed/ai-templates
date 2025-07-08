import os
import sys
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
os.makedirs("data", exist_ok=True)

# Get thread_id from command line argument
if len(sys.argv) < 2:
    print("Usage: python download-conversation-from-thread-id.py <thread_id>")
    sys.exit(1)

thread_id = sys.argv[1]
messages = client.beta.threads.messages.list(thread_id=thread_id, order="asc")

# Create markdown content
markdown_content = []
markdown_content.append(f"# Conversation Thread: {thread_id}")
markdown_content.append(f"Downloaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
markdown_content.append("")

for message in messages.data:
    # Format timestamp
    created_at = datetime.fromtimestamp(message.created_at).strftime('%Y-%m-%d %H:%M:%S')
    
    # Add message header
    role = message.role.capitalize()
    markdown_content.append(f"## {role} - {created_at}")
    markdown_content.append("")
    
    # Process message content
    for content in message.content:
        if hasattr(content, 'text') and content.text:
            text_content = content.text.value
            markdown_content.append(text_content)
            markdown_content.append("")
        elif hasattr(content, 'image_file') and content.image_file:
            file_id = content.image_file.file_id
            markdown_content.append(f"*[Image: {file_id}]*")
            markdown_content.append("")
    
    # Add attachments info if any
    if hasattr(message, 'attachments') and message.attachments:
        markdown_content.append("**Attachments:**")
        for attachment in message.attachments:
            if hasattr(attachment, 'file_id'):
                markdown_content.append(f"- {attachment.file_id}")
        markdown_content.append("")
    
    # Add separator between messages
    markdown_content.append("---")
    markdown_content.append("")

# Save to file
clean_thread_id = thread_id.replace("thread_", "")
filename = f"data/{clean_thread_id}_conversation.md"
with open(filename, "w", encoding="utf-8") as f:
    f.write("\n".join(markdown_content))

print(f"Downloaded conversation to: {filename}")
print(f"Total messages: {len(messages.data)}") 