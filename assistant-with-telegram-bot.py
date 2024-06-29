import openai
from openai import OpenAI
import os
import pandas as pd
from IPython.display import Image
import time
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio  

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TOKEN = os.getenv("TOKEN")
client = OpenAI(api_key=OPENAI_API_KEY, default_headers={"OpenAI-Beta": "assistants=v2"})

# assistant = client.beta.assistants.retrieve('asst_YidtkoYXEnaOoIzvaNw3BCWv')
assistant = client.beta.assistants.retrieve('asst_8ttEhIQdgMr2hlBRZdshFHER')

thread = client.beta.threads.create()

async def run_assistant(question):
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=question,
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    while run.status != "completed":
        await asyncio.sleep(3)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return messages.data[0].content[0].text.value  # Return the assistant's response
    # return messages.data[-1].content[0].text.value  # Return the assistant's latest response


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello there! I\'m a bot. What\'s up?')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Try typing anything and I will do my best to respond!')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command, you can add whatever text you want here.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text.lower()
    print(f"Received message from {update.message.chat}: {text}")
    response: str = await handle_response(text)  # Ensure this is handled asynchronously
    await update.message.reply_text(response)

async def handle_response(text: str) -> str:
    return await run_assistant(text)

# Main execution block
if __name__ == '__main__':
    print('Starting up bot...')
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling()