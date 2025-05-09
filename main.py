import os
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
app = Flask(__name__)

telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()


# /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is working! Send a video file.")


# Video handler
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Video received!")


telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))


@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        telegram_app.update_queue.put_nowait(update)
    return "ok"


@app.route("/", methods=["GET"])
def home():
    return "Service Running"


if __name__ == "__main__":
    telegram_app.run_polling()
