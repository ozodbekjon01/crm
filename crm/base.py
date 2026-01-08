import sqlite3

conn = sqlite3.connect('crm.db')
c = conn.cursor()

# c.execute(""" create table if not exists logins (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     login TEXT UNIQUE NOT NULL,
#     role text DEFAULT 'student' NOT NULL,
#     password TEXT NOT NULL
#     ) """)


# c.execute(""" create table if not exists students (
#     id integer not null,
#     name TEXT NOT NULL,
#     surname TEXT NOT NULL,
#     ochestvo TEXT,
#     phone TEXT,
#     email TEXT,
#     course_id TEXT,
#     date TEXT,
#     foreign key (course_id) references courses(id)
#     foreign key (id) references logins(id)
#     ) """)


# # c.execute(""" insert into students (id, name, surname, ochestvo, phone, email, course_id, date) values
# #     (2, 'Ali', 'Valiyev', "g'ani o'g'li", '+998901234567', 'ali@example.com', '1', '2024-05-01')""")

# c.execute(""" create table if not exists teachers (
#     id integer not null,
#     name TEXT NOT NULL,
#     surname TEXT NOT NULL,
#     ochestvo TEXT,
#     phone TEXT,
#     email TEXT,
#     foreign key (id) references logins(id)
#     ) """)

# c.execute(""" create table if not exists courses (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT NOT NULL,
#     description TEXT,
#     price REAL,
#     teacher_id INTEGER,
#     FOREIGN KEY (teacher_id) REFERENCES teachers(id)
#     ) """)

# # c.execute(""" insert into courses (name, description, price, teacher_id)values ('Matematika', "Boshlang'ich matematika kursi", 100.0, 1)""")


c.execute(""" create table if not exists payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    course_id INTEGER,
    datemm TEXT,
    dateyyyy TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
    ) """)




# # c.execute(""" insert into logins (login, role, password) values
# #     ('super_admin','admin', 'admin123')""")




# c.execute("DROP TABLE IF EXISTS payments")



conn.commit()
conn.close()