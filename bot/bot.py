from os import path
import re

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton,\
ReplyKeyboardMarkup, KeyboardButton

from bot_config import CONFIG
from utils import get_sounds, get_random_sounds, get_authors_by_title
from classes import Sound


sound = None

bot = telebot.TeleBot(CONFIG.get('TOKEN'))

keyboard = ReplyKeyboardMarkup()
keyboard.add(
    KeyboardButton('/start')
)


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

@bot.callback_query_handler(func=lambda cb: 'about' == cb.data)
def handle_about(query):
    bot.send_message(
        query.message.chat.id,
        'This bot allows you to store music in telegram.\nBot created by rogulik, github is https://github.com/rogulikAFC/sound-storage-bot-DRF-telebot'
    )


@bot.callback_query_handler(func=lambda cb: 'search_sound' == cb.data)
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
            InlineKeyboardButton('That\'s it!', callback_data=f'sound_detail_{id}')
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


@bot.callback_query_handler(func=lambda cb: 'rand_sounds' == cb.data)
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


@bot.callback_query_handler(func=lambda cb: 'upload_request' == cb.data)
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

@bot.callback_query_handler(func=lambda cb: 'upload_sound' == cb.data)
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
        message.chat.id,
        'Upload cover image'
    )

    bot.register_next_step_handler(msg, process_upload_sound_cover_step)

def process_upload_sound_cover_step(message):
    global sound

    cover_image_info = None

    try:
        print(message)
        cover_image_info = bot.get_file(message.photo[0].file_id)

    except:
        msg = bot.send_message(
            message.chat.id,
            'You have uploaded not png or jpg file, upload png or jpg file'
        )
        bot.register_next_step_handler(msg, process_upload_sound_cover_step)

    extension_pattern = r'\.[^.]+$'

    extension = re.search(
        extension_pattern, cover_image_info.file_path
    ).group(0)

    file = bot.download_file(cover_image_info.file_path)

    with open(f'new_image{extension}', 'wb') as new_file:
        new_file.write(file)

    file = open(f'new_image{extension}', 'rb')
    sound.cover = file.read()

    msg = bot.send_message(
        message.chat.id,
        'Upload sound file'
    )


    bot.register_next_step_handler(msg, process_upload_sound_file_and_authors_step)

def process_upload_sound_file_and_authors_step(message):
    global sound

    sound_file_info = None

    try:
        sound_file_info = bot.get_file(message.audio.file_id)

    except:
        msg = bot.send_message(
            message.chat.id,
            'You have uploaded not mp3 file, upload mp3 file'
        )
        bot.register_next_step_handler(msg, process_upload_sound_file_and_authors_step)
        return

    file = bot.download_file(sound_file_info.file_path)

    with open('new_file.mp3', 'wb') as new_file:
        new_file.write(file)

    file = open('new_file.mp3', 'rb')
    sound.sound = file.read()

    msg = bot.send_message(
        message.chat.id,
        'Ok, now select authors'
    )

    for author in get_authors_by_title(message.text):  # filters needed
        id = author.get('id')
        title = author.get('title')

        author_keyboard = InlineKeyboardMarkup()
        author_keyboard.add(
            InlineKeyboardButton('That\'s it!', callback_data=f'select_sound_author_{id}')
        )

        bot.send_message(
            message.chat.id,
            title,
            reply_markup=author_keyboard
        )
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton('Yes, upload sound to database', callback_data='upload_sound_to_db')
    )
    keyboard.add(
        InlineKeyboardButton('No, exit', callback_data='upload_sound')
    )

    bot.send_message(
        message.chat.id,
        'Upload sound?',
        reply_markup=keyboard
    )
    

@bot.callback_query_handler(func=lambda cb: cb.data.startswith('select_sound_author_'))
def add_author_to_sound(query):
    id = query.data.split('_')[-1]
    print(id)

    try:
        sound.authors.append(id)

    except:
        bot.send_message(
            query.message.chat.id,
            'Ooops... Somthing went wrong. This error may occur, when you already selected all authors'
        )

    print(sound.title, sound.authors)


@bot.callback_query_handler(func=lambda cb: 'upload_sound_to_db' == cb.data)
def upload_sound_to_db(query):
    global sound

    if sound.upload_to_database():
        bot.send_message(
            query.message.chat.id,
            'Uploaded!'
        )

    else:
        bot.send_message(
            query.message.chat.id,
            'Something went wrong, file not uploaded'
        )

    sound = None


bot.infinity_polling()
