from commands.commands import start

from fastapi import FastAPI, Request
from pydantic import BaseModel
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from dotenv import load_dotenv
import os
import uvicorn

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

app = FastAPI()
telegram_app = Application.builder().token(TOKEN).build()

telegram_app.add_handler(CommandHandler('start', start))


@ app.on_event("startup")
async def on_startup():
    """Initialize the bot and set up the webhook."""
    # Initialize the bot application
    await telegram_app.initialize()

    # Set up the webhook
    # Replace 'your-domain.com' with your actual domain and ensure HTTPS is set up
    webhook_url = "https://e2f3-220-255-223-18.ngrok-free.app/webhook"
    await telegram_app.bot.set_webhook(url=webhook_url)

    # Start the bot (without polling)
    await telegram_app.start()
    print("webhook", webhook_url)
    print("Bot started and webhook set.")


@ app.on_event("shutdown")
async def on_shutdown():
    """Shutdown the bot gracefully."""
    await telegram_app.stop()
    await telegram_app.shutdown()
    print("Bot stopped.")


@ app.get("/")
async def root():
    return {"message": "Telegram bot is running"}


@ app.post("/webhook")
async def telegram_webhook(request: Request):
    """Process incoming webhook updates from Telegram."""
    try:
        data = await request.json()
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.process_update(update)
    except Exception as e:
        print(f"Error processing update: {e}")
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
