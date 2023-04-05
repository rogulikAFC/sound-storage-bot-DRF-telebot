from os import path
import re

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton,\
ReplyKeyboardMarkup, KeyboardButton

from bot_config import CONFIG
from utils import *
from classes import Sound, Album, Author


sound = None
album = None
author = None

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
    # keyboard = InlineKeyboardMarkup()

    # keyboard.add(
    #     InlineKeyboardButton(
    #         'It isn\'t. Show me next 10, please', callback/start_data=f'send_sounds_list_{search_page + 1}'
    #     )
    # )
    # keyboard.add(
    #     InlineKeyboardButton('Back', callback_data='back')    # Not working
    # )

    for sound in Sound.search_sounds(message.text, ):  # pagination and filters needed
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
        'That\'s all',
    )


@bot.callback_query_handler(func=lambda cb: 'sound_detail_' in cb.data)
def sound_detail(query):
    id = query.data.split('_')[-1]
    sound = Sound.get_sound_info(id)

    cover_url = sound.get('cover_url')
    cover = get_cover(cover_url)

    audio_url = sound.get('sound_url')
    audio = Sound.get_sound_file(audio_url)

    authors = ', '.join(author.get('title') for author in sound.get('authors'))

    bot.send_photo(
        query.message.chat.id,
        ('new_image.jpg', cover),
        f'{sound.get("title")} - {authors}'
    )
    bot.send_audio(
        query.message.chat.id,
        audio,
        title=f'{sound.get("title")} - {authors}'
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

    for author in get_authors_by_title(message.text):
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


@bot.callback_query_handler(func=lambda cb: 'search_album' == cb.data)
def search_album(query):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton('Back', callback_data='back')    # Not working
    )

    message = bot.send_message(
        query.message.chat.id,
        'Say me name of album',
        reply_markup=keyboard
    )

    bot.register_next_step_handler(message, process_album_title_step)

def process_album_title_step(message):
    for album in Album.search_albums(message.text):
        id = album.get('id')
        title = album.get('title')
        authors = ', '.join(author.get('title') for author in album.get('authors'))

        album_keyboard = InlineKeyboardMarkup()
        album_keyboard.add(
            InlineKeyboardButton('That\'s it!', callback_data=f'album_detail_{id}')
        )

        bot.send_message(
            message.chat.id,
            f'{title} - {authors}',
            reply_markup=album_keyboard
        )

    bot.send_message(
        message.chat.id,
        'That\'s all',
    )


@bot.callback_query_handler(func=lambda cb: 'album_detail_' in cb.data)
def album_detail(query):
    id = query.data.split('_')[-1]
    album_info = Album.get_album_info(id)

    authors = ', '.join(author.get('title') for author in album_info.get('authors'))
    title = album_info.get('title')

    cover = get_cover(album_info.get('cover_url'))

    bot.send_photo(
        query.message.chat.id,
        ('new_image.jpg', cover),
        f'{title} - {authors}'
    )

    sounds = album_info.get('sounds')

    for sound in sounds:
        id = sound.get('id')
        title = sound.get('title')
        authors = ', '.join(author.get('title') for author in sound.get('authors'))

        sound_keyboard = InlineKeyboardMarkup()
        sound_keyboard.add(
            InlineKeyboardButton('Listen it', callback_data=f'sound_detail_{id}')
        )

        bot.send_message(
            query.message.chat.id,
            f'{title} - {authors}',
            reply_markup=sound_keyboard
        )


@bot.callback_query_handler(func=lambda cb: 'group_album' == cb.data)
def group_album(query):
    msg = bot.send_message(
        query.message.chat.id,
        'Write album title'
    )
    
    bot.register_next_step_handler(msg, group_album_title_step)

def group_album_title_step(message):
    global album
    album = Album(message.text)
    msg = bot.send_message(
        message.chat.id,
        'Upload album cover'
    )

    bot.register_next_step_handler(msg, group_album_cover_step)

def group_album_cover_step(message):
    cover_image_info = None

    try:
        cover_image_info = bot.get_file(message.photo[0].file_id)

    except:
        msg = bot.send_message(
            message.chat.id,
            'You have uploaded not png or jpg file, upload png or jpg file'
        )
        bot.register_next_step_handler(msg, group_album_cover_step)

    extension_pattern = r'\.[^.]+$'

    extension = re.search(
        extension_pattern, cover_image_info.file_path
    ).group(0)

    file = bot.download_file(cover_image_info.file_path)

    with open(f'new_image{extension}', 'wb') as new_file:
        new_file.write(file)

    file = open(f'new_image{extension}', 'rb')
    album.cover = file.read()

    bot.send_message(
        message.chat.id,
        'Select sounds'
    )

    for sound in get_sounds():
        id = sound.get('id')
        title = sound.get('title')
        authors = ', '.join(author.get('title') for author in sound.get('authors'))

        sound_keyboard = InlineKeyboardMarkup()
        sound_keyboard.add(
            InlineKeyboardButton('That\'s it!', callback_data=f'select_album_sound_{id}')
        )

        bot.send_message(
            message.chat.id,
            f'{title} - {authors}',
            reply_markup=sound_keyboard
        )

    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton('Yes, upload album to database', callback_data='upload_album_to_db')
    )
    keyboard.add(
        InlineKeyboardButton('No, exit', callback_data='group_album')
    )


    bot.send_message(
        message.chat.id,
        'Upload album to database?',
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda cb: 'select_album_sound_' in cb.data)
def select_album_sound(query):
    global album

    id = query.data.split('_')[-1]

    try:
        album.sounds.append(id)

    except:
        bot.send_message(
            query.message.chat.id,
            'Ooops... Somthing went wrong. This error may occur, when you already selected all sounds'
        )

    print(album.title, album.sounds)


@bot.callback_query_handler(func=lambda cb: 'upload_album_to_db' == cb.data)
def upload_album_to_db(query):
    global album

    if album.upload_to_database():
        bot.send_message(
            query.message.chat.id,
            'Uploaded!'
        )

    else:
        bot.send_message(
            query.message.chat.id,
            'Something went wrong, album not uploaded'
        )

    album = None


@bot.callback_query_handler(func=lambda cb: 'create_author' == cb.data)
def upload_author(query):
    msg = bot.send_message(
        query.message.chat.id,
        'Write author title'
    )
    
    bot.register_next_step_handler(msg, upload_author_title)

def upload_author_title(message):
    global author
    author = Author(message.text)
    msg = bot.send_message(
        message.chat.id,
        'Upload author description'
    )

    bot.register_next_step_handler(msg, upload_author_description)

def upload_author_description(message):
    global author
    author.description = message.text
    
    if author.upload_to_database():
        bot.send_message(
            message.chat.id,
            'Uploaded!'
        )

    else:
        bot.send_message(
            message.chat.id,
            'Something went wrong, author not created'
        )


@bot.callback_query_handler(func=lambda cb: 'search_author' == cb.data)
def search_author(query):
    msg = bot.send_message(
        query.message.chat.id,
        'Write author title',
    )

    bot.register_next_step_handler(msg, search_author_title_step)

def search_author_title_step(message):
    for author in Author.search_authors(message.text):
        id = author.get('id')
        title = author.get('title')

        author_keyboard = InlineKeyboardMarkup()
        author_keyboard.add(
            InlineKeyboardButton(
                'View this author',
                callback_data=f'author_detail_{id}'
            )
        )

        bot.send_message(
            message.chat.id,
            title,
            reply_markup=author_keyboard
        )

    bot.send_message(
        message.chat.id,
        'That\'s all'
    )


@bot.callback_query_handler(func=lambda cb: 'author_detail_' in cb.data)
def author_detail(query):
    author_id = query.data.split('_')[-1]
    author = Author.get_author_info(author_id)

    bot.send_message(
        query.message.chat.id,
        f'''
        <b> {author.get("title")} </b> \n\n{author.get("description")}
        ''',
        parse_mode='HTML'
    )

    bot.send_message(
        query.message.chat.id,
        '<b> Sounds: </b>',
        parse_mode='HTML'
    )

    for sound in author.get('sounds'):
        id = sound.get('id')
        title = sound.get('title')

        sound_keyboard = InlineKeyboardMarkup()
        sound_keyboard.add(
            InlineKeyboardButton(
                'Listen it', callback_data=f'sound_detail_{id}'
            )
        )

        bot.send_message(
            query.message.chat.id,
            f'{title}',
            reply_markup=sound_keyboard
        )

    bot.send_message(
        query.message.chat.id,
        '<b> Albums: </b>',
        parse_mode='HTML'
    )

    for album in author.get('albums'):
        id = album.get('id')
        title = album.get('title')
        authors = ', '.join(author.get('title') for author in album.get('authors'))

        album_keyboard = InlineKeyboardMarkup()
        album_keyboard.add(
            InlineKeyboardButton(
                'View', callback_data=f'album_detail_{id}'
            )
        )

        bot.send_message(
            query.message.chat.id,
            f'{title} - {authors}',
            reply_markup=album_keyboard
        )


bot.infinity_polling()
