import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler, Dispatcher
import subprocess
import uuid

app = Flask(__name__)

# Telegram Bot setup
TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, update_queue=None, workers=0)

# Define resolutions for video compression
RESOLUTIONS = ["240p", "360p", "480p", "720p", "1080p"]

@app.route('/')
def hello_world():
    return "Telegram Bot is running!"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    # Get the latest update from Telegram
    json_str = request.get_data().decode('UTF-8')
    update = Update.de_json(json_str, bot)
    
    dispatcher.process_update(update)  # Process the update using the dispatcher
    return 'OK'

async def start(update, context):
    await update.message.reply_text("नमस्ते! कृपया अपनी वीडियो फाइल भेजें।")

async def handle_video(update, context):
    file = update.message.video or update.message.document
    if not file:
        await update.message.reply_text("कृपया एक वीडियो फाइल भेजें।")
        return

    file_id = file.file_id
    file_unique_id = file.file_unique_id
    file_path = f"{file_unique_id}.mp4"
    new_file = await context.bot.get_file(file_id)
    await new_file.download_to_drive(file_path)

    context.user_data['file_path'] = file_path

    keyboard = [[InlineKeyboardButton(res, callback_data=res)] for res in RESOLUTIONS]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("कृपया वांछित गुणवत्ता चुनें:", reply_markup=reply_markup)

async def button(update, context):
    query = update.callback_query
    await query.answer()
    resolution = query.data
    file_path = context.user_data.get('file_path')

    if not file_path:
        await query.edit_message_text("कोई वीडियो फाइल नहीं मिली। कृपया पहले एक वीडियो भेजें।")
        return

    output_file = f"converted_{uuid.uuid4()}.mp4"
    resolution_map = {
        "240p": "426x240",
        "360p": "640x360",
        "480p": "854x480",
        "720p": "1280x720",
        "1080p": "1920x1080"
    }
    size = resolution_map.get(resolution, "640x360")

    command = [
        "ffmpeg",
        "-i", file_path,
        "-vf", f"scale={size}",
        "-c:a", "copy",
        output_file
    ]

    try:
        subprocess.run(command, check=True)
        await context.bot.send_video(chat_id=query.message.chat_id, video=open(output_file, 'rb'))
        await query.edit_message_text(f"यह रही आपकी {resolution} वीडियो।")
    except subprocess.CalledProcessError:
        await query.edit_message_text("वीडियो कनवर्ज़न में त्रुटि हुई।")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(output_file):
            os.remove(output_file)

def setup_dispatcher():
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
    dispatcher.add_handler(CallbackQueryHandler(button))

if __name__ == "__main__":
    setup_dispatcher()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
