import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()

# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a video, and I'll compress it!")

application.add_handler(CommandHandler("start", start))

# --- Message Handler (for videos) ---
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Received your video. Compression options coming soon!")

application.add_handler(MessageHandler(filters.Video | filters.Document.VIDEO, handle_video))

# --- Webhook Endpoint ---
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

# --- Home Route ---
@app.route("/")
def home():
    return "Telegram Video Bot is Live!"

# --- Gunicorn Entry Point ---
if __name__ == "__main__":
    app.run(port=10000)
