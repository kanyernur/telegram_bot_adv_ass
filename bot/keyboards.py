from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from translations.translations import translations

def language_markup():
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = [
        InlineKeyboardButton(text='Қазақша 🇰🇿', callback_data='kk'),
        InlineKeyboardButton(text='Русский 🇷🇺', callback_data='ru'),
        InlineKeyboardButton(text='English 🇬🇧', callback_data='en')
    ]
    markup.add(*buttons)
    return markup

def main_menu_markup(language: str):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton(translations[language]['my_students']),
        KeyboardButton(translations[language]['view_isp']),
        KeyboardButton(translations[language]['report_of_grades']),
        KeyboardButton(translations[language]['problem_students'])
    ]
    markup.add(*buttons)
    return markup

def report_types_markup(language: str):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton(translations[language]['first_assessment']),
        KeyboardButton(translations[language]['second_assessment']),
        KeyboardButton(translations[language]['semester']),
        KeyboardButton(translations[language]['back'])
    ]
    markup.add(*buttons)
    return markup
