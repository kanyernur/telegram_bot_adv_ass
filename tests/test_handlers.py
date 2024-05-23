import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from aiogram import types

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot.handlers import process_email, process_password, problem_students
from bot.states import AuthStates
from config.config import config
from translations.translations import translations
from aiogram.dispatcher import FSMContext

class BotTestCase(unittest.TestCase):
    @patch('bot.handlers.process_email')
    def test_process_email(self, mock_process_email):
        # Ваши тесты здесь
        pass

    # Добавьте другие тесты здесь

if __name__ == '__main__':
    unittest.main()
