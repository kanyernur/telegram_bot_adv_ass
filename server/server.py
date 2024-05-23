#server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database.database import fetch_user, check_email, fetch_students, generate_excel_report, generate_pdf_isp

# Создание экземпляра приложения FastAPI
app = FastAPI()

# Модель запроса авторизации
class AuthRequest(BaseModel):
    email: str
    password: str

# Модель ответа авторизации
class AuthResponse(BaseModel):
    advisor_id: int
    name: str

# Модель запроса проверки email
class CheckEmailRequest(BaseModel):
    email: str

# Модель запроса ИУП студента
class StudentISPRequest(BaseModel):
    student_name: str

# Маршрут для авторизации
@app.post("/auth", response_model=AuthResponse)
def authenticate(auth_request: AuthRequest):
    user = fetch_user(auth_request.email, auth_request.password)    # Получение пользователя из БД по email и паролю
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")    # Ошибка при неверном email или пароле
    return AuthResponse(advisor_id=user['advisor_id'], name=user['name'])   # Возвращение ответа с данными пользователя

# Маршрут для проверки существования email
@app.post("/auth/check_email")
def check_email_endpoint(auth_request: CheckEmailRequest):
    user = check_email(auth_request.email)  # Проверка email в БД
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")  # Ошибка при отсутствии email в БД
    return {"detail": "Email exists"}   # Возвращение ответа о существовании email

# Маршрут для получения списка студентов по ID адвайзера
@app.get("/students/{advisor_id}")
def get_students(advisor_id: int):
    students = fetch_students(advisor_id)   # Получение списка студентов для данного адвайзера
    if students:
        report_file = generate_excel_report(advisor_id)     # Генерация отчета по студентам
        return {"report_file": report_file}     # Возвращение пути к отчету
    else:
        raise HTTPException(status_code=404, detail="No students found")    # Ошибка при отсутствии студентов

# Маршрут для получения ИУП студента
@app.post("/student_isp")
def get_student_isp(student_isp_request: StudentISPRequest):
    report_file = generate_pdf_isp(student_isp_request.student_name)    # Генерация PDF-отчета по ИУП студента
    if not report_file:
        raise HTTPException(status_code=404, detail="Student not found or no courses registered")   # Ошибка при отсутствии студента или курсов
    return {"report_file": report_file}     # Возвращение пути к отчету

# Маршрут для получения отчета по ID адвайзера
@app.get("/report/{advisor_id}")
def get_report(advisor_id: int):
    report_file = generate_excel_report(advisor_id)     # Генерация отчета по студентам
    return {"report_file": report_file}     # Возвращение пути к отчету

# Основной блок запуска сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)     # Запуск сервера на хосте 0.0.0.0 и порту 8000
