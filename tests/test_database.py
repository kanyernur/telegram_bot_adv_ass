import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.database import (
    get_db_connection,
    fetch_grades,
    generate_assessment_report,
    fetch_problem_students,
    fetch_problem_students_based_on_electives,
    is_semester_closed
)

class TestDatabase(unittest.TestCase):
    @patch('database.database.get_db_connection')
    def test_fetch_grades(self, mock_get_db_connection):
        # Ваши тесты здесь
        pass

    # Добавьте другие тесты здесь

if __name__ == '__main__':
    unittest.main()
