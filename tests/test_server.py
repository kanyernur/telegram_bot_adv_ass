# tests/test_server.py
import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from server.server import app

client = TestClient(app)

class TestServer(unittest.TestCase):

    @patch('server.server.fetch_user')
    def test_authenticate_success(self, mock_fetch_user):
        mock_fetch_user.return_value = {'advisor_id': 1, 'name': 'Test User'}
        response = client.post("/auth", json={"email": "test@example.com", "password": "password"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"advisor_id": 1, "name": "Test User"})

    @patch('server.server.fetch_user')
    def test_authenticate_failure(self, mock_fetch_user):
        mock_fetch_user.return_value = None
        response = client.post("/auth", json={"email": "test@example.com", "password": "wrong_password"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid email or password"})

    @patch('server.server.check_email')
    def test_check_email_exists(self, mock_check_email):
        mock_check_email.return_value = {'email': 'test@example.com'}
        response = client.post("/auth/check_email", json={"email": "test@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"detail": "Email exists"})

    @patch('server.server.check_email')
    def test_check_email_not_exists(self, mock_check_email):
        mock_check_email.return_value = None
        response = client.post("/auth/check_email", json={"email": "test@example.com"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Email not found"})

    @patch('server.server.fetch_students')
    @patch('server.server.generate_excel_report')
    def test_get_students_success(self, mock_generate_excel_report, mock_fetch_students):
        mock_fetch_students.return_value = [{'student_id': 1, 'name': 'Student 1'}]
        mock_generate_excel_report.return_value = 'report.xlsx'
        response = client.get("/students/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"report_file": "report.xlsx"})

    @patch('server.server.fetch_students')
    def test_get_students_not_found(self, mock_fetch_students):
        mock_fetch_students.return_value = []
        response = client.get("/students/1")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "No students found"})

    @patch('server.server.generate_pdf_isp')
    def test_get_student_isp_success(self, mock_generate_pdf_isp):
        mock_generate_pdf_isp.return_value = 'isp_report.pdf'
        response = client.post("/student_isp", json={"student_name": "Student 1"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"report_file": "isp_report.pdf"})

    @patch('server.server.generate_pdf_isp')
    def test_get_student_isp_not_found(self, mock_generate_pdf_isp):
        mock_generate_pdf_isp.return_value = None
        response = client.post("/student_isp", json={"student_name": "Student 1"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Student not found or no courses registered"})

if __name__ == '__main__':
    unittest.main()
