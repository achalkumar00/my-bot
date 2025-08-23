import os
import telegram
from flask import Flask, request

# Bot Token ko Environment Variable se lena
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable not set!")

# Bot aur Flask app ko initialize karna
bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

@app.route("/")
def index():
    """
    Yeh function root URL (/) par ek message dikhayega.
    Isse Render check kar payega ki service live hai.
    """
    return "Bot is live and running!", 200

@app.route(f"/{TOKEN}", methods=["POST"])
def respond():
    """Yeh function Telegram se aane wale updates ko handle karega."""
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    # Sirf text messages ko process karna
    if update.message and update.message.text:
        chat_id = update.message.chat.id
        msg_id = update.message.message_id
        text = update.message.text.lower()

        # /start command ke liye handler
        if text == "/start":
            bot.sendMessage(chat_id=chat_id, text="Hello! Main Flask par chal raha hoon.", reply_to_message_id=msg_id)
    
    return "ok", 200

@app.route("/set_webhook", methods=['GET', 'POST'])
def set_webhook():
    """
    Webhook set karne ke liye. Deploy hone ke baad, aapko browser mein
    https://your-app-name.onrender.com/set_webhook par ek baar jaana hoga.
    """
    # Webhook URL aapke Render ke URL se banega
    # Service 'live' hone ke baad hi set karein
    webhook_url = f'https://{request.host}/{TOKEN}'
    s = bot.set_webhook(webhook_url)
    if s:
        return f"Webhook setup successful: {webhook_url}"
    else:
        return "Webhook setup failed!"

if __name__ == "__main__":
    # Yeh sirf local testing ke liye hai, Render isko use nahi karega
    app.run(threaded=True)

