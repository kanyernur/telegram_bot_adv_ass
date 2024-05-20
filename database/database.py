import psycopg2
from psycopg2.extras import RealDictCursor
from config.config import config
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from fpdf import FPDF

def get_db_connection():
    connection = psycopg2.connect(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT
    )
    return connection

def fetch_user(email, password):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT * FROM advisors WHERE email = %s AND password = %s", (email, password)
    )
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user

def check_email(email):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT * FROM advisors WHERE email = %s", (email,)
    )
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user

def fetch_students(advisor_id):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT * FROM students WHERE advisor_id = %s", (advisor_id,)
    )
    students = cursor.fetchall()
    cursor.close()
    connection.close()
    return students

def generate_excel_report(advisor_id):
    students = fetch_students(advisor_id)
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Student Report'

    # Заголовки
    headers = ['№', 'ФИО', 'Курс', 'ИИН', 'Email', 'Телефон']
    sheet.append(headers)

    # Стиль заголовков
    header_font = Font(bold=True)
    header_fill = PatternFill(start_color="FFC000", end_color="FFC000", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")

    for cell in sheet["1:1"]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment

    # Заполнение данных
    row_num = 2
    for idx, student in enumerate(students, start=1):
        sheet.append([idx, f"{student['surname']} {student['name']}", 4, student['iin'], student['email'], student['phone']])

        # Стиль данных
        for col_num in range(1, 7):
            cell = sheet.cell(row=row_num, column=col_num)
            cell.alignment = Alignment(horizontal="center", vertical="center")

        if row_num % 2 == 0:
            fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
        else:
            fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")

        for col_num in range(1, 7):
            sheet.cell(row=row_num, column=col_num).fill = fill

        row_num += 1

    # Авторазмер колонок
    for col in sheet.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        sheet.column_dimensions[column].width = adjusted_width

    report_file = f"report_{advisor_id}.xlsx"
    workbook.save(report_file)
    return report_file

class PDF(FPDF):
    pass

def generate_pdf_isp(student_name):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        """
        SELECT s.name, s.surname, c.code, c.name as course_name, c.credits, c.semester
        FROM students s
        JOIN student_semester_courses ssc ON s.student_id = ssc.student_id
        JOIN courses c ON ssc.course_id = c.course_id
        WHERE s.name || ' ' || s.surname = %s
        ORDER BY c.semester
        """, (student_name,)
    )
    results = cursor.fetchall()
    cursor.close()
    connection.close()

    pdf = PDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.add_font('DejaVuB', '', 'DejaVuSansCondensed-Bold.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)

    if results:
        full_name = f"{results[0]['name']} {results[0]['surname']}"
        pdf.cell(200, 10, txt=full_name, ln=True, align='C')
        semesters = {}

        for result in results:
            semester = result['semester']
            course_details = {
                'code': result['code'],
                'name': result['course_name'],
                'credits': result['credits']
            }
            if semester not in semesters:
                semesters[semester] = []
            semesters[semester].append(course_details)

        for semester, courses in semesters.items():
            pdf.set_font("DejaVuB", '', 12)
            pdf.cell(200, 10, txt=f"Семестр {semester}", ln=True)
            pdf.set_font("DejaVu", '', 12)
            pdf.cell(60, 10, txt="Код дисциплины", border=1, ln=False)
            pdf.cell(100, 10, txt="Дисциплины", border=1, ln=False)
            pdf.cell(30, 10, txt="Кредиты", border=1, ln=True)
            for course in courses:
                pdf.cell(60, 10, txt=course['code'], border=1, ln=False)
                pdf.cell(100, 10, txt=course['name'], border=1, ln=False)
                pdf.cell(30, 10, txt=str(course['credits']), border=1, ln=True)
    else:
        pdf.cell(200, 10, txt="Студент не найден или не зарегистрирован на курсы", ln=True)

    report_file = f"ISP_{student_name}.pdf"
    pdf.output(report_file, 'F')
    return report_file
