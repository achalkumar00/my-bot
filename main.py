import os
import requests
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler

# Bot Token ko Environment Variable se lena
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable not set!")

# Bot ko initialize karna
bot = Bot(token=TOKEN)

# Flask app
app = Flask(__name__)

# Dispatcher ko set karna (updates ko handle karne ke liye)
dispatcher = Dispatcher(bot, None, use_context=True)

# /start command ke liye function
def start(update, context):
    """Jab /start command aayega toh yeh message bhejega."""
    update.message.reply_text("Hello! Main ab stable version par chal raha hoon.")

# /status command ke liye function
def status(update, context):
    """Render status check karne ke liye inline button ke sath."""
    keyboard = [
        [InlineKeyboardButton("Check Render Status", callback_data='check_status')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Render service ka status check karne ke liye button dabaye:', reply_markup=reply_markup)

# Callback ke liye function
def button_callback(update, context):
    query = update.callback_query
    query.answer()

    # Render public status page check
    try:
        response = requests.get("https://status.render.com/api/v2/status.json", timeout=5)
        data = response.json()
        status = data.get("status", {}).get("description", "Status not found")
        message = f"Render Status: {status}"
    except Exception as e:
        message = "Status fetch karne mein error aayi. Try again later."

    query.edit_message_text(text=message)

# Dispatcher mein command handler ko add karna
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("status", status))
dispatcher.add_handler(CallbackQueryHandler(button_callback))

@app.route("/")
def index():
    """Render ko batane ke liye ki service live hai."""
    return "Bot is live and running!", 200

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook_handler():
    """Webhook is route par Telegram se updates receive karega."""
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok", 200

@app.route("/set_webhook", methods=['GET'])
def set_webhook():
    """Webhook set karne ke liye."""
    host = request.host_url # Yeh 'https://my-bot-1-yeh7.onrender.com/' jaisa hoga
    webhook_url = os.path.join(host, TOKEN)
    bot.set_webhook(webhook_url)
    return f"Webhook set successfully to {webhook_url}", 200
