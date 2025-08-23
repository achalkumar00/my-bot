import os
import telegram
import asyncio
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
    """Yeh function root URL (/) par ek message dikhayega."""
    return "Bot is live and running!", 200

@app.route(f"/{TOKEN}", methods=["POST"])
def respond():
    """Yeh function Telegram se aane wale updates ko handle karega."""
    try:
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        if update.message and update.message.text:
            chat_id = update.message.chat.id
            text = update.message.text.lower()

            if text == "/start":
                # yahan bot.send_message async hai, isliye asyncio.run() use karein
                asyncio.run(bot.send_message(chat_id=chat_id, text="Hello! Main Flask par chal raha hoon."))
    except Exception as e:
        print(f"Error processing update: {e}")
    
    return "ok", 200

@app.route("/set_webhook", methods=['GET', 'POST'])
def set_webhook():
    """
    Webhook set karne ke liye. Deploy hone ke baad, aapko browser mein
    https://your-app-name.onrender.com/set_webhook par ek baar jaana hoga.
    """
    webhook_url = f'https://{request.host}/{TOKEN}'
    
    # Yahan hum asyncio.run() ka istemal karke async function ko chala rahe hain
    # Yeh corrected part hai
    s = asyncio.run(bot.set_webhook(webhook_url))
    
    if s:
        return f"Webhook setup successful: {webhook_url}"
    else:
        return "Webhook setup failed!"

# Render gunicorn use karega, isliye is block ki zaroorat nahi hai
# if __name__ == "__main__":
#     app.run(threaded=True)

