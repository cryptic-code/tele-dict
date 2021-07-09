import os
from custom_logging import get_logger
from load_config import get_reply
from dotenv import load_dotenv
import requests
import telegram
from flask import Flask, request

load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
APP_URL = os.getenv('APP_URL')

API_BASE_URL = 'https://api.dictionaryapi.dev/api/v2/entries/en_US/'

logger = get_logger(__name__, only_debug=True)

bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

def start_cmd_handler(chat_id: telegram.Chat.id) -> None:
    reply = get_reply('START_MSG')
    bot.send_message(chat_id=chat_id, text=reply, parse_mode='markdown')

def define_cmd_handler(chat_id: telegram.Chat.id) -> None:
    reply = get_reply('DEFINE_ERR')
    bot.send_message(chat_id=chat_id, text=reply, parse_mode='markdown')

def help_cmd_handler(chat_id: telegram.Chat.id) -> None:
    reply = get_reply('HELP_MSG')
    bot.send_message(chat_id=chat_id, text=reply, parse_mode='markdown')

def dict_req_handler(msg_txt: str, chat_id: telegram.Chat.id) -> None:
    _, search_key = msg_txt.lower().split("define ")

    if len(search_key.split(' ')) > 1:
        bot.send_message(chat_id=chat_id, text=get_reply('WORD_ERR'))
    else:
        logger.info(f"Fetching definition for {search_key}")

        search_url = API_BASE_URL + search_key
        response = requests.get(search_url)

        if response:
            data = response.json()[0]

            defined_word = data['word']
            phonetic_txt = data['phonetics'][0]['text']
            phonetic_audio = data['phonetics'][0]['audio']

            bot.send_message(chat_id=chat_id, text=get_reply('PHONETICS_MSG', {'defined_word': defined_word, 'phonetic_txt': phonetic_txt, 'phonetic_audio': phonetic_audio}), parse_mode='markdown')

            for object_ in data['meanings']:
                part_of_speech = object_['partOfSpeech']
                definition = object_['definitions'][0]['definition']
                example = str(object_['definitions'][0].get('example'))

                bot.send_message(chat_id=chat_id, text=get_reply('DEFINITION_MSG', {'part_of_speech': part_of_speech, 'definition': definition, 'example': example}), parse_mode='markdown')
        else:
            bot.send_message(chat_id=chat_id, text=get_reply("WORD_ERR"), parse_mode="markdown")

def edits_handler(chat_id: telegram.Chat.id):
    bot.send_message(chat_id=chat_id, text=get_reply('EDITS_REPLY'), parse_mode='markdown')

def unrecognized_handler(chat_id: telegram.Chat.id):
    bot.send_message(chat_id=chat_id, text=get_reply('UNRECOGNIZED'), parse_mode='markdown')

def attachment_handler(chat_id: telegram.Chat.id):
    bot.send_message(chat_id=chat_id, text=get_reply('ATTACHMENTS_ERR'), parse_mode='markdown')

@app.route("/")
def index():
    bot.set_webhook(url=APP_URL+'telegram-dict', drop_pending_updates=True)
    return "Hello, World!"

@app.route('/telegram-dict', methods=["POST", "GET"])
def handle_request():
    if request.method == 'POST':
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        chat_id = update.effective_chat.id
        
        if update.edited_message:
            edits_handler(chat_id)
            return "OK"

        if update.chat_member or update.my_chat_member:
            return "OK"

        if update.effective_message.effective_attachment:
            attachment_handler(chat_id)
            return "OK"

        msg_id = update.effective_message.message_id
        msg_txt = update.message.text.encode('utf-8').decode()

        logger.info(f"Received message: {msg_txt}")

        if msg_txt == '/start':
            start_cmd_handler(chat_id)
        elif msg_txt.startswith('/define'):
            define_cmd_handler(chat_id)
        elif msg_txt.startswith('/help'):
            help_cmd_handler(chat_id)
        elif msg_txt.lower().startswith('define '):
            dict_req_handler(msg_txt, chat_id)
        else:
            unrecognized_handler(chat_id)

        return "OK"
    else:
        return "Hello, world! ;)"