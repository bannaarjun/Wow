import os
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()

# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a video, and I'll compress it!")

application.add_handler(CommandHandler("start", start))

# --- Message Handler for video and doc/video ---
video_filter = filters.VIDEO | filters.Document.MimeType("video/mp4")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Video received! (Compression logic coming soon)")

application.add_handler(MessageHandler(video_filter, handle_video))

# --- Webhook route ---
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

# --- Root route ---
@app.route("/")
def home():
    return "Bot is running!"

# --- Entry point ---
if __name__ == "__main__":
    app.run(port=10000)
