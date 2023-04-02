import requests

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot_config import CONFIG
from utils import get_sounds, get_random_sounds
from classes import Sound


bot = telebot.TeleBot(CONFIG.get('TOKEN'))


@bot.message_handler(commands=['start'])
def handle_start(message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton('Search sound', callback_data='search_sound')
    )
    keyboard.add(
        InlineKeyboardButton('Get 10 random sounds', callback_data='rand_sounds')
    )

    keyboard.add(
        InlineKeyboardButton('Search author', callback_data='search_author')
    )
    keyboard.add(
        InlineKeyboardButton('Search album', callback_data='search_album')
    )

    keyboard.add(
        InlineKeyboardButton('Wanna upload something?', callback_data='upload_request')
    )
    keyboard.add(
        InlineKeyboardButton('About', callback_data='about')
    )

    bot.send_message(
        message.chat.id,
        f'Hello, {message.from_user.first_name}!',
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda cb: 'about')
def handle_about(query):
    bot.send_message(
        query.message.chat.id,
        'This bot allows you to store music in telegram.\nBot created by rogulik, github is https://github.com/rogulikAFC/sound-storage-bot-DRF-telebot'
    )


@bot.callback_query_handler(func=lambda cb: 'search_sound' in cb.data)
def handle_search_sound_cb(query):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton('Back', callback_data='back')    # Not working
    )

    message = bot.send_message(
        query.message.chat.id,
        'Say me name of sound',
        reply_markup=keyboard
    )

    bot.register_next_step_handler(message, process_sound_title_step)

def process_sound_title_step(message):
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            'It isn\'t. Show me next 10, please', callback_data='send_sounds_list'
        )
    )
    keyboard.add(
        InlineKeyboardButton('Back', callback_data='back')    # Not working
    )

    for sound in get_sounds():  # pagination and filters needed
        id = sound.get('id')
        title = sound.get('title')
        authors = ', '.join(author.get('title') for author in sound.get('authors'))

        sound_keyboard = InlineKeyboardMarkup()
        sound_keyboard.add(
            InlineKeyboardButton('That\'s is!', callback_data=f'sound_detail_{id}')
        )

        bot.send_message(
            message.chat.id,
            f'{title} - {authors}',
            reply_markup=sound_keyboard
        )

    bot.send_message(
        message.chat.id,
        'Is there your sound?',
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda cb: 'rand_sounds')
def handle_random_sounds(query):    # need to create endpoint
    for sound in get_random_sounds():
        id = sound.get('id')
        title = sound.get('title')
        authors = ', '.join(author.get('title') for author in sound.get('authors'))

        sound_keyboard = InlineKeyboardMarkup()
        sound_keyboard.add(
            InlineKeyboardButton('Listen to it!', callback_data=f'sound_detail_{id}')
        )

        bot.send_message(
            query.message.chat.id,
            f'{title} - {authors}',
            reply_markup=sound_keyboard
        )

    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton('Next 10', callback_data='rand_sound')
    )
    keyboard.add(
        InlineKeyboardButton('Back', callback_data='back')
    )

    bot.send_message(
        query.message.chat.id,
        'That\'s all',
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda cb: 'upload_request' in cb.data)
def handle_upload_request(query):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton('Sound', callback_data='upload_sound')
    )
    keyboard.add(
        InlineKeyboardButton('Group album from sounds', callback_data='group_album')
    )
    keyboard.add(
        InlineKeyboardButton('Create new author', callback_data='create_author')
    )
    keyboard.add(
        InlineKeyboardButton('Back', callback_data='back')
    )

    bot.send_message(
        query.message.chat.id,
        'What do you want to upload?',
        reply_markup=keyboard
    )


sound = None

@bot.callback_query_handler(func=lambda cb: 'upload_sound' in cb.data)
def handle_upload_sound(query):
    message = bot.send_message(
        query.message.chat.id,
        'Write sound name'
    )

    bot.register_next_step_handler(message, process_upload_sound_title_step)

def process_upload_sound_title_step(message):
    global sound
    sound = Sound(message.text)

    msg = bot.send_message(
        msg.chat.id,
        'Upload sound file'
    )
    

bot.infinity_polling()
