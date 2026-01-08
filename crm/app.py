
from datetime import timedelta ,date
import sqlite3
from flask import app, redirect, render_template, request, session
from datetime import datetime

app = app.Flask(__name__)
app.secret_key = 'your_secret_key'
app.permanent_session_lifetime =  timedelta(minutes=30)

#============================== LOGIN ROUTE ==============================
@app.route('/', methods=['GET', 'POST'])
@app.route("/login",  methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        conn= sqlite3.connect('crm.db')
        c = conn.cursor()

        c.execute("SELECT * FROM logins WHERE login=? AND password=?", (login, password))
        user = c.fetchone()

        if user:
            session['user'] = user[0]
            session['user_name'] = user[1]  # shu yerda nom saqlanadi
            session['role'] = user[2]
            return redirect(f'/{user[2]}')
        else:
            error = "Login yoki parol noto'g'ri"
            return render_template('login.html', error=error)
    return render_template('login.html')



@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


#============================== teacher ==============================

@app.route('/teacher')
def teacher():
    if 'user' in session and session['role'] == 'teacher':
        return render_template('teacher_dashboard.html')
    else:
        return redirect('/login')

#============================== admin ==============================
@app.route('/admin')
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user' not in session or session['role'] != 'admin':
        return redirect('/login')

    year = date.today().year
    conn = sqlite3.connect('crm.db')
    c = conn.cursor()

    courses = c.execute("""
        SELECT c.id, c.name, c.price,
               t.name, t.surname
        FROM courses c
        LEFT JOIN teachers t ON t.id = c.teacher_id
    """).fetchall()

    dashboard = []

    for course_id, course_name, price, tname, tsurname in courses:
        students = c.execute("""
            SELECT id, name, surname, date
            FROM students
            WHERE course_id = ?
        """, (course_id,)).fetchall()

        table = []

        for sid, sname, ssurname, start_date in students:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            row = {"student": f"{sname} {ssurname}", "months": []}

            for m in range(1, 13):
                paid = c.execute("""
                    SELECT 1 FROM payments
                    WHERE student_id=? AND course_id=?
                    AND datemm=? AND dateyyyy=?
                """, (sid, course_id, str(m).zfill(2), str(year))).fetchone()

                if paid:
                    status = "paid"
                else:
                    cell_date = date(year, m, 1)
                    today = date.today()

                    if cell_date < start.date() or cell_date > today:
                        status = "none"
                    else:
                        status = "late"

                row["months"].append(status)

            table.append(row)

        dashboard.append({
            "course": course_name,
            "price": price,
            "teacher": f"{tname} {tsurname}",
            "table": table
        })

    conn.close()
    return render_template(
        'admin_dashboard.html',
        dashboard=dashboard,
        year=year
    )


@app.route('/admin/cources')
def admin_cources():
    if 'user' in session and session['role'] == 'admin':
        conn = sqlite3.connect('crm.db')
        c = conn.cursor()
        c.execute("SELECT * FROM courses")
        courses = c.fetchall()
        c.execute("SELECT * FROM teachers")
        teachers = c.fetchall()
        conn.close()
        return render_template('admin_cources.html', courses=courses, teachers=teachers)
    else:
        return redirect('/login')

@app.route('/admin/courses/edit', methods=['GET', 'POST'])
def edit_cources():
    if 'user' in session and session['role'] == 'admin':
        conn = sqlite3.connect('crm.db')
        c = conn.cursor()
        c.execute("SELECT * FROM courses")
        courses = c.fetchall()
        conn.close()
        return render_template('edit_cources.html', courses=courses)
    else:
        return redirect('/login') 

@app.route("/admin/courses/add", methods=['GET', 'POST'])
def add_courses():
    if 'user' not in session or session.get('role') != 'admin':
        return redirect('/login')

    conn = sqlite3.connect('crm.db')
    c = conn.cursor()
    teachers = c.execute(
        "SELECT id, name, surname FROM teachers"
    ).fetchall()
    conn.close()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        teacher_id = request.form['teacher']

        conn = sqlite3.connect('crm.db')
        c = conn.cursor()
        c.execute("""
            INSERT INTO courses (name, description, price, teacher_id)
            VALUES (?, ?, ?, ?)
        """, (name, description, price, teacher_id))
        conn.commit()
        conn.close()

        return redirect('/admin/cources')

    return render_template('add_course.html', teachers=teachers)




@app.route('/admin/courses/edit/<int:course_id>', methods=['GET', 'POST'])
def admin_courses_edit(course_id):
    if 'user' not in session or session.get('role') != 'admin':
        return redirect('/login')

    conn = sqlite3.connect('crm.db')
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        teacher_id = request.form['teacher']

        c.execute("""
            UPDATE courses 
            SET name=?, description=?, price=?, teacher_id=? 
            WHERE id=?
        """, (name, description, price, teacher_id, course_id))

        conn.commit()
        conn.close()
        return redirect('/admin/cources')

    # GET qismi
    c.execute("SELECT * FROM courses WHERE id=?", (course_id,))
    course = c.fetchone()

    c.execute("SELECT * FROM teachers")
    teachers = c.fetchall()

    conn.close()
    return render_template('edit_course.html', course=course, teachers=teachers)


@app.route('/admin/students')
def admin_students():   
    if 'user' in session and session['role'] == 'admin':
        conn = sqlite3.connect('crm.db')
        c = conn.cursor()
        students =c.execute("SELECT * FROM students").fetchall()
        courses=c.execute("SELECT * FROM courses").fetchall()
        conn.close()
        return render_template('admin_students.html', students=students, courses=courses)
    else:
        return redirect('/login')


@app.route('/admin/students/add', methods=['GET', 'POST'])
def admin_students_add():
    if 'user' in session and session['role'] == 'admin':
        
        conn = sqlite3.connect('crm.db')
        c = conn.cursor()
        courses=c.execute("SELECT * FROM courses").fetchall()
        conn.close()
        
        
        if request.method == 'POST':
            login = request.form['login']
            password = request.form['password']
            name = request.form['name']
            surname = request.form['surname']
            ochestvo = request.form['ochestvo']
            phone = request.form['phone']
            email = request.form['email']
            course_id = request.form.get('course')  # .get() xato bermaydi
            time = datetime.now().strftime("%Y-%m-%d")
            if not course_id:
                # xatolikni qayta ishlash yoki default qiymat berish
                return "Kurs tanlanmagan!", 400
            
            conn = sqlite3.connect('crm.db')
            c = conn.cursor()
            c.execute("INSERT INTO logins (login, role, password) VALUES (?, 'student', ?)", (login, password))
            student_id = c.lastrowid
            c.execute("""INSERT INTO students (id, name, surname, ochestvo, phone, email, course_id, date) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (student_id, name, surname, ochestvo, phone, email, course_id, time))
            conn.commit()
            conn.close()
            return redirect('/admin/students')
        return render_template('add_student.html', courses=courses)
    else:
        return redirect('/login')

@app.route('/admin/students/edit', methods=['GET', 'POST'])
def admin_students_edit():
    if 'user' in session and session['role'] == 'admin':
        conn = sqlite3.connect('crm.db')
        c = conn.cursor()
        students =c.execute("SELECT * FROM students").fetchall()
        courses=c.execute("SELECT * FROM courses").fetchall()
        conn.close()
        return render_template('edit_student.html', students=students, courses=courses)
    else:
        return redirect('/login')
    
    
    
@app.route('/admin/students/view/<int:student_id>', methods=['GET', 'POST'])
def admin_students_view(student_id):
    if 'user' not in session or session['role'] != 'admin':
        return redirect('/login')

    with sqlite3.connect('crm.db') as conn:
        c = conn.cursor()

        if request.method == 'POST':
            name = request.form['name']
            surname = request.form['surname']
            ochestvo = request.form['ochestvo']
            phone = request.form['phone']
            email = request.form['email']
            course_id = request.form.get('course')

            c.execute("""
                UPDATE students 
                SET name=?, surname=?, ochestvo=?, phone=?, email=?, course_id=? 
                WHERE id=?
            """, (name, surname, ochestvo, phone, email, course_id, student_id))

            conn.commit()
            return redirect('/admin/students')

        # GET qismi
        c.execute("SELECT * FROM students WHERE id=?", (student_id,))
        student = c.fetchone()

        c.execute("SELECT * FROM courses")
        courses = c.fetchall()

    return render_template('edit_stud.html', student=student, courses=courses)

@app.route('/admin/courses/students/<int:course_id>', methods=['GET', 'POST'])
def admin_courses_students(course_id):
    if 'user' not in session or session['role'] != 'admin':
        return redirect('/login')

    conn = sqlite3.connect('crm.db')
    c = conn.cursor()

    c.execute("SELECT * FROM students WHERE course_id=?", (course_id,))
    students = c.fetchall()

    c.execute("SELECT * FROM courses WHERE id=?", (course_id,))
    course = c.fetchone()
    conn.close()
    
    return render_template('course_students.html', students=students, course=course)
   
@app.route("/admin/students/delete/<int:student_id>", methods=["GET", "POST"])
def admin_students_delete(student_id):
    if 'user' in session and session['role'] == 'admin':
        conn = sqlite3.connect('crm.db')
        c = conn.cursor()
        c.execute("DELETE FROM students WHERE id=?", (student_id,))
        c.execute("DELETE FROM logins WHERE id=?", (student_id,))
        conn.commit()
        conn.close()
        return redirect('/admin/students')
    else:
        return redirect('/login')
    
    
    
@app.route("/admin/courses/delete/<int:course_id>", methods=['GET', 'POST'])
def admin_cources_delete(course_id):
    if 'user' in session and session['role'] == 'admin':
        conn = sqlite3.connect('crm.db')
        c = conn.cursor()
        c.execute("DELETE FROM courses WHERE id=?", (course_id,))
        conn.commit()
        conn.close()
        return redirect('/admin/cources')
    else:
        return redirect('/login')



@app.route('/admin/teachers')
def admin_teachers():   
    if 'user' in session and session['role'] == 'admin':
        conn = sqlite3.connect('crm.db')
        c = conn.cursor()
        teachers =c.execute("SELECT * FROM teachers").fetchall()
        courses=c.execute("SELECT * FROM courses").fetchall()
        conn.close()
        return render_template('admin_teachers.html', teachers=teachers, courses=courses)
    else:
        return redirect('/login')
  
@app.route('/admin/teachers/add', methods=['GET', 'POST'])
def admin_teachers_add():
    if 'user' not in session or session.get('role') != 'admin':
        return redirect('/login')

    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        name = request.form['name']
        surname = request.form['surname']
        ochestvo = request.form.get('ochestvo')
        phone = request.form.get('phone')
        email = request.form.get('email')

        conn = sqlite3.connect('crm.db')
        c = conn.cursor()

        # login jadvaliga qo‘shish
        c.execute(
            "INSERT INTO logins (login, role, password) VALUES (?, ?, ?)",
            (login, 'teacher', password)
        )

        teacher_id = c.lastrowid

        # teachers jadvaliga qo‘shish
        c.execute("""
            INSERT INTO teachers (id, name, surname, ochestvo, phone, email)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (teacher_id, name, surname, ochestvo, phone, email))

        conn.commit()
        conn.close()

        return redirect('/admin/teachers')

    return render_template('add_teacher.html')


@app.route('/admin/teachers/edit', methods=['GET', 'POST'])
def admin_teachers_edit():
    if 'user' in session and session['role'] == 'admin':
        conn = sqlite3.connect('crm.db')
        c = conn.cursor()
        teachers =c.execute("SELECT * FROM teachers").fetchall()
        courses=c.execute("SELECT * FROM courses").fetchall()
        conn.close()
        return render_template('edit_teachers.html', teachers=teachers, courses=courses)
    else:
        return redirect('/login')
  
@app.route("/admin/teachers/delete/<int:teacher_id>", methods=["GET", "POST"])
def admin_teachers_delete(teacher_id):
    if 'user' in session and session['role'] == 'admin':
        conn = sqlite3.connect('crm.db')
        c = conn.cursor()
        c.execute("DELETE FROM teachers WHERE id=?", (teacher_id,))
        c.execute("DELETE FROM logins WHERE id=?", (teacher_id,))
        conn.commit()
        conn.close()
        return redirect('/admin/teachers')
    else:
        return redirect('/login')
    
@app.route('/admin/teachers/view/<int:teacher_id>', methods=['GET', 'POST'])
def admin_teachers_view(teacher_id):
    if 'user' not in session or session['role'] != 'admin':
        return redirect('/login')

    with sqlite3.connect('crm.db') as conn:
        c = conn.cursor()

        if request.method == 'POST':
            name = request.form['name']
            surname = request.form['surname']
            ochestvo = request.form['ochestvo']
            phone = request.form['phone']
            email = request.form['email']

            c.execute("""
                UPDATE teachers 
                SET name=?, surname=?, ochestvo=?, phone=?, email=? 
                WHERE id=?
            """, (name, surname, ochestvo, phone, email, teacher_id))

            conn.commit()
            return redirect('/admin/teachers')

        # GET qismi
        c.execute("SELECT * FROM teachers WHERE id=?", (teacher_id,))
        teacher = c.fetchone()
        c.execute("select * from logins where id=?", (teacher_id,))
        login_info = c.fetchone()

    return render_template('edit_teacher.html', teacher=teacher, login_info=login_info)  


@app.route('/admin/payments')
def admin_payments():
    if 'user' not in session or session['role'] != 'admin':
        return redirect('/login')

    student = request.args.get('student', '')
    course = request.args.get('course', '')
    month = request.args.get('month', '')
    year = request.args.get('year', '')

    conn = sqlite3.connect('crm.db')
    c = conn.cursor()

    # SELECT uchun asosiy query
    query = """
        SELECT 
            p.id,
            s.name || ' ' || s.surname AS student_name,
            c.name AS course_name,
            p.datemm,
            p.dateyyyy
        FROM payments p
        JOIN students s ON s.id = p.student_id
        JOIN courses c ON c.id = p.course_id
        WHERE 1=1
    """
    params = []

    if student:
        query += " AND (s.name LIKE ? OR s.surname LIKE ?)"
        params.extend([f"%{student}%", f"%{student}%"])

    if course:
        query += " AND c.name LIKE ?"
        params.append(f"%{course}%")

    if month:
        query += " AND p.datemm = ?"
        params.append(month)

    if year:
        query += " AND p.dateyyyy = ?"
        params.append(year)

    payments = c.execute(query, params).fetchall()

    # SELECT uchun mavjud oy va yillar
    months = c.execute(
        "SELECT DISTINCT datemm FROM payments ORDER BY datemm"
    ).fetchall()

    years = c.execute(
        "SELECT DISTINCT dateyyyy FROM payments ORDER BY dateyyyy"
    ).fetchall()

    conn.close()

    return render_template(
        'admin_payments.html',
        payments=payments,
        months=months,
        years=years,
        selected_month=month,
        selected_year=year
    )


@app.route('/admin/payments/auto', methods=['GET', 'POST'])
def admin_payments_auto():
    if 'user' not in session or session['role'] != 'admin':
        return redirect('/login')

    conn = sqlite3.connect('crm.db')
    c = conn.cursor()

    students = c.execute(
        "SELECT id, name, surname FROM students"
    ).fetchall()

    result = None

    if request.method == 'POST':
        student_id = request.form['student_id']

        # O‘quvchining kursi va boshlangan sanasi
        c.execute("""
            SELECT s.course_id, c.name, s.date
            FROM students s
            JOIN courses c ON c.id = s.course_id
            WHERE s.id = ?
        """, (student_id,))
        row = c.fetchone()

        if not row:
            conn.close()
            return "O‘quvchi topilmadi", 404

        course_id, course_name, start_date = row

        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        y, m = start_dt.year, start_dt.month

        # To‘langan oylar
        paid = c.execute("""
            SELECT datemm, dateyyyy
            FROM payments
            WHERE student_id=? AND course_id=?
        """, (student_id, course_id)).fetchall()

        paid_set = {(int(m), int(y)) for m, y in paid}

        today = date.today()

        # Keyingi to‘lanishi kerak bo‘lgan oy
        while (m, y) in paid_set:
            m += 1
            if m == 13:
                m = 1
                y += 1

            if y > today.year or (y == today.year and m > today.month):
                break

        result = [{
            "student_id": student_id,
            "course_id": course_id,
            "course_name": course_name,
            "next_month": str(m).zfill(2),
            "next_year": str(y)
        }]

    conn.close()
    return render_template(
        'admin_payment_auto.html',
        students=students,
        result=result
    )



@app.route('/admin/payments/confirm', methods=['POST'])
def admin_payments_confirm():
    if 'user' not in session or session['role'] != 'admin':
        return redirect('/login')

    confirms = request.form.getlist('confirm[]')

    conn = sqlite3.connect('crm.db')
    c = conn.cursor()

    for item in confirms:
        course_id, month, year, student_id = item.split('|')

        c.execute("""
            INSERT INTO payments (student_id, course_id, datemm, dateyyyy)
            VALUES (?, ?, ?, ?)
        """, (student_id, course_id, month, year))

    conn.commit()
    conn.close()

    return redirect('/admin/payments')

       
#============================== student ==============================

@app.route('/student')
def student():
    if 'user' in session and session['role'] == 'student':
        return render_template('student_dashboard.html')
    else:
        return redirect('/login')



if __name__ == '__main__':
    app.run(debug=True)