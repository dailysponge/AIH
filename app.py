from commands.commands import start, add_friend, show_leaderboard, notify_friends, handle_user_message, handle_user_image

from fastapi import FastAPI, Request
from pydantic import BaseModel
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv
import os
import uvicorn

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

app = FastAPI()
telegram_app = Application.builder().token(TOKEN).build()

user_data = {}  # Move this here, after all imports

# Update these lines to pass user_data
telegram_app.add_handler(CommandHandler(
    'start', lambda update, context: start(update, context, user_data)))
telegram_app.add_handler(CommandHandler(
    'add_friend', lambda update, context: add_friend(update, context, user_data)))
telegram_app.add_handler(CommandHandler(
    'leaderboard', lambda update, context: show_leaderboard(update, context, user_data)))
telegram_app.add_handler(CommandHandler(
    'notify_friends', lambda update, context: notify_friends(update, context, user_data)))

# Update this line to handle both text and photo messages
telegram_app.add_handler(MessageHandler(
    filters.TEXT,
    lambda update, context: handle_user_message(update, context, user_data)
))

telegram_app.add_handler(MessageHandler(
    filters.PHOTO,
    lambda update, context: handle_user_image(update, context, user_data)
))


@ app.on_event("startup")
async def on_startup():
    """Initialize the bot and set up the webhook."""
    # Initialize the bot application
    await telegram_app.initialize()

    # Set up the webhook
    # Replace 'your-domain.com' with your actual domain and ensure HTTPS is set up
    webhook_url = "https://8b59-220-255-223-18.ngrok-free.app/webhook"
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
