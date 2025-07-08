import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
os.makedirs("data", exist_ok=True)

# Get thread_id from command line argument
if len(sys.argv) < 2:
    print("Usage: python download-responses-api-files-from-thread-id.py <thread_id>")
    sys.exit(1)
thread_id = sys.argv[1]
messages = client.beta.threads.messages.list(thread_id=thread_id)

image_counter = 1
attachment_counter = 1
downloaded_files = []
for message in messages.data:
    for content in message.content:
        if hasattr(content, 'image_file') and content.image_file:
            file_id = content.image_file.file_id
            file_content = client.files.content(file_id)
            clean_thread_id = thread_id.replace("thread_", "")
            clean_file_id = file_id.replace("file-", "")
            filename = f"data/{clean_thread_id}_image_{image_counter}_{clean_file_id}.png"
            with open(filename, "wb") as f:
                f.write(file_content.read())
            downloaded_files.append(filename)
            image_counter += 1
    if hasattr(message, 'attachments') and message.attachments:
        for attachment in message.attachments:
            if hasattr(attachment, 'file_id'):
                file_id = attachment.file_id
                file_content = client.files.content(file_id)
                clean_thread_id = thread_id.replace("thread_", "")
                clean_file_id = file_id.replace("file-", "")
                filename = f"data/{clean_thread_id}_attachment_{attachment_counter}_{clean_file_id}.png"
                with open(filename, "wb") as f:
                    f.write(file_content.read())
                downloaded_files.append(filename)
                attachment_counter += 1
print(f"Downloaded {len(downloaded_files)} files:")
for filename in downloaded_files:
    print(f"  {filename}")