from aiogram.dispatcher.filters.state import State, StatesGroup

class AuthStates(StatesGroup):
    choosing_language = State()
    waiting_for_email = State()
    waiting_for_password = State()

class MenuStates(StatesGroup):
    main_menu = State()  # Новое состояние для главного меню
    waiting_for_student_name = State()
    waiting_for_report_type = State()  # Новое состояние для меню "Отчет об оценке"
