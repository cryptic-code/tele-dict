from os import getenv
from custom_logging import get_logger
from botness import bot, dp
from telegram import Update
from dotenv import load_dotenv
from flask import Flask, request

load_dotenv()

APP_URL = getenv('APP_URL')
ADMIN_PASS = getenv('ADMIN_PASS')

logger = get_logger(__name__, only_debug=True)

app = Flask(__name__)

@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        try:
            if request.headers['deleteWebhook'] == ADMIN_PASS:
                bot.delete_webhook(drop_pending_updates=True)
                return "Bye, bye!"
        except:
            return "POST request!?"
    else:
        try:
            if request.headers['setWebhook'] == ADMIN_PASS:
                bot.set_webhook(url=APP_URL+'telegram-dict', drop_pending_updates=True)
                return "Hola!"
        except:
            return "Hello, World!"

@app.route('/telegram-dict', methods=["POST", "GET"])
def handle_request():
    if request.method == 'POST':
        update = Update.de_json(request.get_json(force=True), bot)
        dp.process_update(update)
        return "OK"
    else:
        return "Hello, world! ;)"