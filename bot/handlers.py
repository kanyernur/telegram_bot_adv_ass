#handlers.py
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from aiogram.types import InputFile
from bot.states import AuthStates, MenuStates
from bot.keyboards import language_markup, main_menu_markup, report_types_markup
from config.config import config
from translations.translations import translations
import requests
from database.database import generate_assessment_report, is_semester_closed

API_TOKEN = config.API_TOKEN
SERVER_URL = config.SERVER_URL

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

user_sessions = {}


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await choose_language(message)


async def choose_language(message: types.Message):
    await AuthStates.choosing_language.set()
    await message.reply(
        f"{translations['en']['choose_language']}\n{translations['kk']['choose_language']}\n{translations['ru']['choose_language']}",
        reply_markup=language_markup()
    )


@dp.callback_query_handler(lambda c: c.data in ['kk', 'ru', 'en'], state=AuthStates.choosing_language)
async def set_language(callback_query: types.CallbackQuery, state: FSMContext):
    language = callback_query.data
    user_id = callback_query.from_user.id
    user_sessions[user_id] = {'language': language}
    await state.update_data(language=language)
    await bot.send_message(user_id, translations[language]['welcome'])
    await bot.send_message(user_id, translations[language]['enter_email'])
    await AuthStates.waiting_for_email.set()


@dp.message_handler(state=AuthStates.waiting_for_email)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text
    language = user_sessions[message.from_user.id]['language']
    if '@' not in email or '.' not in email:
        await message.reply(translations[language]['invalid_email'])
        return

    response = requests.post(f"{SERVER_URL}/auth/check_email", json={"email": email})
    if response.status_code == 200:
        await state.update_data(email=email)
        await AuthStates.waiting_for_password.set()
        await message.reply(translations[language]['enter_password'])
    else:
        await message.reply(translations[language]['invalid_email'])


@dp.message_handler(state=AuthStates.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    password = message.text
    user_data = await state.get_data()
    email = user_data['email']
    language = user_sessions[message.from_user.id]['language']

    response = requests.post(f"{SERVER_URL}/auth", json={"email": email, "password": password})
    if response.status_code == 200:
        user = response.json()
        user_sessions[message.from_user.id].update(user)
        await message.reply(translations[language]['authorization_success'])
        await show_main_menu(message, language)
        await state.finish()
    else:
        await message.reply(translations[language]['invalid_password'])
        await AuthStates.waiting_for_password.set()


async def show_main_menu(message: types.Message, language: str):
    await bot.send_message(message.from_user.id, translations[language]['main_menu'],
                           reply_markup=main_menu_markup(language))


@dp.message_handler(lambda message: message.text in [translations[lang]['my_students'] for lang in translations.keys()], state='*')
async def my_students(message: types.Message):
    language = user_sessions[message.from_user.id]['language']
    advisor_id = user_sessions[message.from_user.id]['advisor_id']
    response = requests.get(f"{SERVER_URL}/students/{advisor_id}")
    if response.status_code == 200:
        with open(response.json()["report_file"], 'rb') as file:
            await message.reply_document(file)
    else:
        await message.reply(translations[language]['authorization_failed'])


# Пример вашей функции авторизации
@dp.message_handler(lambda message: message.text in [translations[lang]['view_isp'] for lang in translations.keys()], state='*')
async def view_isp(message: types.Message):
    language = user_sessions[message.from_user.id]['language']
    await bot.send_message(message.from_user.id, translations[language]['enter_student_name'])
    await MenuStates.waiting_for_student_name.set()

@dp.message_handler(state=MenuStates.waiting_for_student_name)
async def process_student_name(message: types.Message, state: FSMContext):
    student_name = message.text

    response = requests.post(f"{SERVER_URL}/student_isp", json={"student_name": student_name})
    if response.status_code == 200:
        with open(response.json()["report_file"], 'rb') as file:
            await message.reply_document(file)
        await state.finish()
    else:
        await message.reply("Авторизация не удалась. Попробуйте снова.")


@dp.message_handler(lambda message: message.text in [translations[lang]['report_of_grades'] for lang in translations.keys()], state='*')
async def report_of_grades(message: types.Message):
    language = user_sessions[message.from_user.id]['language']
    await bot.send_message(message.from_user.id, translations[language]['choose_option'], reply_markup=report_types_markup(language))
    await MenuStates.waiting_for_report_type.set()

@dp.message_handler(lambda message: message.text in [translations[lang]['back'] for lang in translations.keys()], state=MenuStates.waiting_for_report_type)
async def back_to_main_menu(message: types.Message, state: FSMContext):
    language = user_sessions[message.from_user.id]['language']
    await bot.send_message(message.from_user.id, translations[language]['main_menu'], reply_markup=main_menu_markup(language))
    await MenuStates.main_menu.set()

@dp.message_handler(state=MenuStates.waiting_for_report_type)
async def grades_menu_handler(message: types.Message, state: FSMContext):
    language = user_sessions[message.from_user.id]['language']
    if message.text == translations[language]['first_assessment']:
        report_file = generate_assessment_report(1)  # Генерация отчета для 1 аттестации
        await bot.send_document(message.chat.id, InputFile(report_file))
    elif message.text == translations[language]['second_assessment']:
        report_file = generate_assessment_report(2)  # Генерация отчета для 2 аттестации
        await bot.send_document(message.chat.id, InputFile(report_file))
    elif message.text == translations[language]['semester']:
        if is_semester_closed():
            report_file = generate_assessment_report(3)  # Генерация отчета для семестрового отчета, если семестр закрыт
            await bot.send_document(message.chat.id, InputFile(report_file))
        else:
            # Ответ о том, что семестр еще не окончен
            await bot.send_message(message.from_user.id, translations[language]['semester_not_finished'])


def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
