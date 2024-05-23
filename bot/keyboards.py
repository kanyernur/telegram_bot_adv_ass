#keyboards.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from translations.translations import translations

# Функция для создания разметки клавиатуры для выбора языка
def language_markup():
    # Создание объекта InlineKeyboardMarkup с шириной строки 3 кнопки
    markup = InlineKeyboardMarkup(row_width=3)
    # Создание кнопок для выбора языка
    buttons = [
        InlineKeyboardButton(text='Қазақша 🇰🇿', callback_data='kk'),    # Кнопка для казахского языка
        InlineKeyboardButton(text='Русский 🇷🇺', callback_data='ru'),    # Кнопка для русского языка
        InlineKeyboardButton(text='English 🇬🇧', callback_data='en')     # Кнопка для английского языка
    ]
    # Добавление кнопок в разметку
    markup.add(*buttons)
    return markup   # Возврат разметки клавиатуры

# Функция для создания разметки главного меню в зависимости от выбранного языка
def main_menu_markup(language: str):
    # Создание объекта ReplyKeyboardMarkup с изменением размера клавиатуры
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    # Создание кнопок главного меню
    buttons = [
        KeyboardButton(translations[language]['my_students']),      # Кнопка "Мои студенты"
        KeyboardButton(translations[language]['view_isp']),         # Кнопка "Посмотреть ИУП студента"
        KeyboardButton(translations[language]['report_of_grades']), # Кнопка "Отчет об оценках"
        KeyboardButton(translations[language]['problem_students'])  # Кнопка "Проблемные студенты"
    ]
    # Добавление кнопок в разметку
    markup.add(*buttons)
    return markup   # Возврат разметки клавиатуры

# Функция для создания разметки меню выбора типа отчета в зависимости от выбранного языка
def report_types_markup(language: str):
    # Создание объекта ReplyKeyboardMarkup с изменением размера клавиатуры
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    # Создание кнопок для выбора типа отчета
    buttons = [
        KeyboardButton(translations[language]['first_assessment']),     # Кнопка "1 аттестация"
        KeyboardButton(translations[language]['second_assessment']),    # Кнопка "2 аттестация"
        KeyboardButton(translations[language]['semester']),             # Кнопка "Семестровый"
        KeyboardButton(translations[language]['back'])                  # Кнопка "Назад"
    ]
    # Добавление кнопок в разметку
    markup.add(*buttons)
    return markup   # Возврат разметки клавиатуры
