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
from database.database import generate_assessment_report, is_semester_closed, fetch_problem_students, \
    fetch_problem_students_based_on_electives, fetch_students, generate_excel_report

# Инициализация токена и URL сервера из конфигурационного файла
API_TOKEN = config.API_TOKEN
SERVER_URL = config.SERVER_URL

# Настройка логирования для отображения информации
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера с использованием токена и памяти для хранения состояний FSM
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Добавление промежуточного слоя логирования для диспетчера
dp.middleware.setup(LoggingMiddleware())

# Словарь для хранения сессий пользователей
user_sessions = {}

# Обработчик команды /start, запускает выбор языка
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await choose_language(message)

# Функция для запроса выбора языка у пользователя
async def choose_language(message: types.Message):
    await AuthStates.choosing_language.set()
    await message.reply(
        f"{translations['en']['choose_language']}\n{translations['kk']['choose_language']}\n{translations['ru']['choose_language']}",
        reply_markup=language_markup()
    )


# Обработчик выбора языка из callback-запроса
@dp.callback_query_handler(lambda c: c.data in ['kk', 'ru', 'en'], state=AuthStates.choosing_language)
async def set_language(callback_query: types.CallbackQuery, state: FSMContext):
    language = callback_query.data # Получение выбранного языка
    user_id = callback_query.from_user.id # Получение ID пользователя
    user_sessions[user_id] = {'language': language} # Сохранение выбранного языка в сессии пользователя
    await state.update_data(language=language) # Обновление данных состояния
    await bot.send_message(user_id, translations[language]['welcome']) # Приветственное сообщение на выбранном языке
    await bot.send_message(user_id, translations[language]['enter_email']) # Запрос ввода email
    await AuthStates.waiting_for_email.set()    # Установка состояния ожидания email

# Обработчик ввода email пользователя
@dp.message_handler(state=AuthStates.waiting_for_email)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text    # Получение введенного email
    language = user_sessions[message.from_user.id]['language']  # Получение выбранного языка пользователя
    if '@' not in email or '.' not in email:    # Проверка валидности email
        await message.reply(translations[language]['invalid_email'])    # Сообщение о недействительном email
        return

    # Отправка запроса на проверку email на сервере
    response = requests.post(f"{SERVER_URL}/auth/check_email", json={"email": email})
    if response.status_code == 200: # Если email существует
        await state.update_data(email=email)    # Обновление данных состояния
        await AuthStates.waiting_for_password.set() # Установка состояния ожидания пароля
        await message.reply(translations[language]['enter_password'])   # Запрос ввода пароля
    else:
        await message.reply(translations[language]['invalid_email'])    # Сообщение о недействительном email

# Обработчик ввода пароля пользователя
@dp.message_handler(state=AuthStates.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    password = message.text # Получение введенного пароля
    user_data = await state.get_data()  # Получение данных состояния
    email = user_data['email']  # Получение email из данных состояния
    language = user_sessions[message.from_user.id]['language']  # Получение выбранного языка пользователя

    # Отправка запроса на авторизацию на сервере
    response = requests.post(f"{SERVER_URL}/auth", json={"email": email, "password": password})
    if response.status_code == 200: # Если авторизация успешна
        user = response.json()  # Получение данных пользователя
        user_sessions[message.from_user.id].update(user)    # Обновление данных сессии пользователя
        await message.reply(translations[language]['authorization_success'])    # Сообщение об успешной авторизации
        await show_main_menu(message, language) # Показ главного меню
        await state.finish()    # Завершение состояния
    else:
        await message.reply(translations[language]['invalid_password']) # Сообщение о недействительном пароле
        await AuthStates.waiting_for_password.set() # Установка состояния ожидания пароля

# Функция для показа главного меню
async def show_main_menu(message: types.Message, language: str):
    await bot.send_message(message.from_user.id, translations[language]['main_menu'],
                           reply_markup=main_menu_markup(language)) # Отправка сообщения с главным меню и соответствующей клавиатурой


# Обработчик кнопки "Мои студенты"
@dp.message_handler(lambda message: message.text in [translations[lang]['my_students'] for lang in translations.keys()], state='*')
async def my_students(message: types.Message):
    language = user_sessions[message.from_user.id]['language']
    advisor_id = user_sessions[message.from_user.id]['advisor_id']
    students = fetch_students(advisor_id)
    if students:
        report_file = generate_excel_report(advisor_id)
        await message.reply_document(InputFile(report_file))
    else:
        await message.reply(translations[language]['no_students'])


# Обработчик кнопки "Посмотреть ИУП студента"
@dp.message_handler(lambda message: message.text in [translations[lang]['view_isp'] for lang in translations.keys()], state='*')
async def view_isp(message: types.Message):
    language = user_sessions[message.from_user.id]['language'] # Получение выбранного языка пользователя
    await bot.send_message(message.from_user.id, translations[language]['enter_student_name'])  # Запрос ввода имени студента
    await MenuStates.waiting_for_student_name.set() # Установка состояния ожидания имени студента


# Обработчик ввода имени студента
@dp.message_handler(state=MenuStates.waiting_for_student_name)
async def process_student_name(message: types.Message, state: FSMContext):
    student_name = message.text # Получение введенного имени студента

    # Отправка запроса на получение ИУП студента
    response = requests.post(f"{SERVER_URL}/student_isp", json={"student_name": student_name})
    if response.status_code == 200: # Если запрос успешен
        with open(response.json()["report_file"], 'rb') as file:
            await message.reply_document(file)   # Отправка документа с ИУП студента
        await state.finish()    # Завершение состояния
    else:
        await message.reply("Авторизация не удалась. Попробуйте снова.")    # Сообщение о неудачной авторизации


# Обработчик кнопки "Отчет об оценках"
@dp.message_handler(lambda message: message.text in [translations[lang]['report_of_grades'] for lang in translations.keys()], state='*')
async def report_of_grades(message: types.Message):
    language = user_sessions[message.from_user.id]['language']
    advisor_id = user_sessions[message.from_user.id]['advisor_id']
    await bot.send_message(message.from_user.id, translations[language]['choose_option'], reply_markup=report_types_markup(language))
    await MenuStates.waiting_for_report_type.set()


# Обработчик кнопки "Назад" в меню отчетов
@dp.message_handler(lambda message: message.text in [translations[lang]['back'] for lang in translations.keys()], state=MenuStates.waiting_for_report_type)
async def back_to_main_menu(message: types.Message, state: FSMContext):
    language = user_sessions[message.from_user.id]['language']  # Получение выбранного языка пользователя
    await bot.send_message(message.from_user.id, translations[language]['main_menu'], reply_markup=main_menu_markup(language))  # Возврат в главное меню
    await MenuStates.main_menu.set()    # Установка состояния главного меню


# Обработчик выбора типа отчета
@dp.message_handler(state=MenuStates.waiting_for_report_type)
async def grades_menu_handler(message: types.Message, state: FSMContext):
    language = user_sessions[message.from_user.id]['language']
    advisor_id = user_sessions[message.from_user.id]['advisor_id']
    if message.text == translations[language]['first_assessment']:
        report_file = generate_assessment_report(advisor_id, 1)
        await bot.send_document(message.chat.id, InputFile(report_file))
    elif message.text == translations[language]['second_assessment']:
        report_file = generate_assessment_report(advisor_id, 2)
        await bot.send_document(message.chat.id, InputFile(report_file))
    elif message.text == translations[language]['semester']:
        if is_semester_closed():
            report_file = generate_assessment_report(advisor_id, 3)
            await bot.send_document(message.chat.id, InputFile(report_file))
        else:
            await bot.send_message(message.from_user.id, translations[language]['semester_not_finished'])


# Обработчик кнопки "Проблемные студенты"
@dp.message_handler(lambda message: message.text in [translations[lang]['problem_students'] for lang in translations.keys()], state='*')
async def problem_students(message: types.Message):
    language = user_sessions[message.from_user.id]['language']
    advisor_id = user_sessions[message.from_user.id]['advisor_id']
    problem_students = fetch_problem_students(advisor_id)
    elective_problem_students = fetch_problem_students_based_on_electives(advisor_id)

    response_message_assessment = translations[language]['problem_students_header'] + "\n"
    for student in problem_students:
        full_name = f"{student['surname']} {student['name']}"
        for assessment in student['assessments']:
            response_message_assessment += f"{full_name} {translations[language]['assessment_problem'].format(score=assessment['score'], course_name=assessment['course_name'], assessment_number=assessment['assessment_number'])}"

    response_message_attendance = translations[language]['problem_students_header'] + "\n"
    for student in problem_students:
        full_name = f"{student['surname']} {student['name']}"
        for attendance in student['attendances']:
            response_message_attendance += f"{full_name} {translations[language]['attendance_problem'].format(course_name=attendance['course_name'], percentage=attendance['percentage'])}"

    response_message_elective = translations[language]['problem_students_header'] + "\n"
    for student in elective_problem_students:
        full_name = f"{student['surname']} {student['name']}"
        course_list = ", ".join(student['courses'])
        block_number = student['block_number']
        response_message_elective += f"{full_name} {translations[language]['elective_problem']}: {block_number}: {course_list}.\n"

    if response_message_assessment.strip() != translations[language]['problem_students_header']:
        await message.reply(response_message_assessment)

    if response_message_attendance.strip() != translations[language]['problem_students_header']:
        await message.reply(response_message_attendance)

    if response_message_elective.strip() != translations[language]['problem_students_header']:
        await message.reply(response_message_elective)

# Главная функция запуска бота
def main():
    executor.start_polling(dp, skip_updates=True)   # Запуск процесса polling для получения обновлений



if __name__ == '__main__':
    main()  # Вызов главной функции при запуске скрипта