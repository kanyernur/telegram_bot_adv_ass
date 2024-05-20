# config.py

import os


class Config:
    # Получаем параметры подключения из переменных окружения для безопасности
    DB_NAME = os.getenv('DB_NAME', 'advisor_help')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '2003')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')

    # Конфигурация для Telegram API
    API_TOKEN = os.getenv('API_TOKEN', '6907442840:AAFaaL1jxgSwwo7aw2sHy9v6kjDrwO0sdoc')
    SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:8000')


config = Config()
