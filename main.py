import os
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import asyncio

BOT_TOKEN = os.environ.get("BOT_TOKEN")
app = Flask(__name__)

# Create Application
application: Application = ApplicationBuilder().token(BOT_TOKEN).build()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is working! Send a video file.")

# video handler
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Video received!")

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    # convert incoming request to telegram update
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return "ok"

@app.route("/")
def home():
    return "Bot is running."

if __name__ == "__main__":
    app.run(port=10000)
