from os import getenv
from load_config import get_reply
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext, MessageHandler, Filters
import requests

TOKEN = getenv('TELEGRAM_TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, None, workers=0)

API_BASE_URL = 'https://api.dictionaryapi.dev/api/v2/entries/en_US/'

def start_cmd_handler(update: Update, context: CallbackContext) -> None:
    """ Handle `/start` command """

    reply = get_reply('START_CMD')
    context.bot.send_message(chat_id=update.effective_message.chat_id, text=reply, parse_mode='markdown')

def define_cmd_handler(update: Update, context: CallbackContext) -> None:
    """ Handle /define coommand """

    reply = get_reply('DEFINE_CMD')
    context.bot.send_message(chat_id=update.effective_message.chat_id, text=reply, parse_mode='markdown')

def help_cmd_handler(update: Update, context: CallbackContext) -> None:
    """ Handle /help command """

    reply = get_reply('HELP_CMD')
    context.bot.send_message(chat_id=update.effective_message.chat_id, text=reply, parse_mode='markdown')

def dict_req_handler(update: Update, context: CallbackContext) -> None:
    """ Handle `define <word>` message """

    chat_id = update.effective_message.chat_id
    msg_txt = update.effective_message.text.encode('utf-8').decode()
    _, search_key = msg_txt.lower().split("define ")

    if len(search_key.split(' ')) > 1:
        context.bot.send_message(chat_id=chat_id, text=get_reply('INVALID_ERR'))
    else:

        search_url = API_BASE_URL + search_key
        response = requests.get(search_url)

        if response: #check if response is valid 200-400
            data = response.json()[0]

            defined_word = data['word']
            phonetic_txt = data['phonetics'][0]['text']
            phonetic_audio = data['phonetics'][0]['audio']

            context.bot.send_message(chat_id=chat_id, text=get_reply('PHONETICS_MSG', {'defined_word': defined_word, 'phonetic_txt': phonetic_txt, 'phonetic_audio': phonetic_audio}), parse_mode='markdown')

            for object_ in data['meanings']:
                part_of_speech = object_['partOfSpeech']
                definition = object_['definitions'][0]['definition']
                example = str(object_['definitions'][0].get('example'))

                context.bot.send_message(chat_id=chat_id, text=get_reply('DEFINITION_MSG', {'part_of_speech': part_of_speech, 'definition': definition, 'example': example}), parse_mode='markdown')
        else:
            context.bot.send_message(chat_id=chat_id, text=get_reply("INVALID_ERR"), parse_mode="markdown")

def edits_handler(update: Update, context: CallbackContext) -> None:
    """ Handle edited messages. """

    context.bot.send_message(chat_id=update.effective_message.chat_id, text=get_reply('EDIT_ERR'), parse_mode='markdown')

def unrecognized_handler(update: Update, context: CallbackContext) -> None:
    """ Handle unrecognized messages. """

    context.bot.send_message(chat_id=update.effective_message.chat_id, text=get_reply('UNRECOGNIZED_ERR'), parse_mode='markdown')

def attachment_handler(update: Update, context: CallbackContext) -> None:
    """ Handle attachments. """
    
    context.bot.send_message(chat_id=update.effective_message.chat_id, text=get_reply('ATTACHMENT_ERR'), parse_mode='markdown')

dp.add_handler(CommandHandler(command='start', callback=start_cmd_handler, filters=(~Filters.update.edited_message)))
dp.add_handler(CommandHandler(command='define', callback=define_cmd_handler, filters=(~Filters.update.edited_message)))
dp.add_handler(CommandHandler(command='help', callback=help_cmd_handler, filters=(~Filters.update.edited_message)))
dp.add_handler(MessageHandler(filters=(Filters.text & (~Filters.command) & (~Filters.update.edited_message)), callback=dict_req_handler))
dp.add_handler(MessageHandler(filters=(Filters.update.edited_message), callback=edits_handler))
dp.add_handler(MessageHandler(filters=(Filters.attachment), callback=attachment_handler))
dp.add_error_handler(unrecognized_handler)