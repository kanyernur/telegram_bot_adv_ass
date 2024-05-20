#SERVAK
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database.database import fetch_user, check_email, fetch_students, generate_excel_report, generate_pdf_isp

app = FastAPI()

class AuthRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    advisor_id: int
    name: str

class CheckEmailRequest(BaseModel):
    email: str

class StudentISPRequest(BaseModel):
    student_name: str

@app.post("/auth", response_model=AuthResponse)
def authenticate(auth_request: AuthRequest):
    user = fetch_user(auth_request.email, auth_request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return AuthResponse(advisor_id=user['advisor_id'], name=user['name'])

@app.post("/auth/check_email")
def check_email_endpoint(auth_request: CheckEmailRequest):
    user = check_email(auth_request.email)
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    return {"detail": "Email exists"}

@app.get("/students/{advisor_id}")
def get_students(advisor_id: int):
    students = fetch_students(advisor_id)
    if students:
        report_file = generate_excel_report(advisor_id)
        return {"report_file": report_file}
    else:
        raise HTTPException(status_code=404, detail="No students found")

@app.post("/student_isp")
def get_student_isp(student_isp_request: StudentISPRequest):
    report_file = generate_pdf_isp(student_isp_request.student_name)
    if not report_file:
        raise HTTPException(status_code=404, detail="Student not found or no courses registered")
    return {"report_file": report_file}

@app.get("/report/{advisor_id}")
def get_report(advisor_id: int):
    report_file = generate_excel_report(advisor_id)
    return {"report_file": report_file}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
