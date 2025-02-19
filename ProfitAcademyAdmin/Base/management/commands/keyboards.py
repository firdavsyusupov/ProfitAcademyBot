from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from .configs import regions


def contact_button():

    return ReplyKeyboardMarkup([[KeyboardButton("📞Telefon raqamni yuborish", request_contact=True)]], resize_keyboard=True, one_time_keyboard=True)


def apply_course(course_id=None):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅Kursga yozilish", callback_data=f"apply_{course_id}")
        ]
    ])


def payment(promo=True, course_id=None):

    button = []

    if promo is True:
        button.append([InlineKeyboardButton("🎟Menda promokod bor", callback_data="promocode")])

    button.append([InlineKeyboardButton("💸️️️️️️To'lov qilish", callback_data=f"payment_{course_id}")])

    return InlineKeyboardMarkup(button)


def regions_button():

    keyboard = [
        [InlineKeyboardButton(regions[i], callback_data=regions[i]) if i < len(regions)
         else InlineKeyboardButton(" ", callback_data=" ") for i in range(j, j + 2)]
        for j in range(0, len(regions), 2)
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


def course_buttons(courses):
    keyboard = []

    for i in range(0, len(courses), 2):
        row = [courses[i]['title']]

        if i + 1 < len(courses):
            row.append(courses[i + 1]['title'])

        keyboard.append(row)

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


def check_button(user_id, photo_id, course_id):

    callback_data_approve = f"approve.{user_id}.{photo_id}.{course_id}"
    callback_data_reject = f"reject.{user_id}.{photo_id}.{course_id}"

    keyboard = [[
        InlineKeyboardButton("✅", callback_data=callback_data_approve),
        InlineKeyboardButton("🚫", callback_data=callback_data_reject)
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup

def channel_button(url):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Kanalga o'tish", url=url)
        ]
    ])

def skip_button():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("O'tkazib yuborish", callback_data="skip")
        ]
    ])

def admin_button(url):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Admin bilan bog'lanish", url=url)
        ]
    ])