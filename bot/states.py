#states.py
from aiogram.dispatcher.filters.state import State, StatesGroup

# Определение состояний для процесса авторизации
class AuthStates(StatesGroup):
    choosing_language = State()     # Состояние выбора языка
    waiting_for_email = State()     # Состояние ожидания ввода email
    waiting_for_password = State()  # Состояние ожидания ввода пароля

# Определение состояний для меню и взаимодействий после авторизации
class MenuStates(StatesGroup):
    main_menu = State()  # Состояние главного меню
    waiting_for_student_name = State()  # Состояние ожидания ввода имени студента
    waiting_for_report_type = State()  # Состояние ожидания выбора типа отчета
    grades_menu = State()   # Состояние меню оценки
