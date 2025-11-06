import sqlite3
import os

# Удаляем старую базу, если есть
if os.path.exists("courses_enrollments.db"):
    os.remove("courses_enrollments.db")

# Подключаемся
conn = sqlite3.connect("courses_enrollments.db")
cursor = conn.cursor()

# Создаем таблицы
cursor.executescript("""
CREATE TABLE Courses (
    course_id INTEGER PRIMARY KEY,
    course_title TEXT
);

CREATE TABLE Enrollments (
    enrollment_id INTEGER PRIMARY KEY,
    student_id INTEGER,
    course_id INTEGER,
    enrollment_date TEXT,
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);
""")

# Добавляем тестовые данные
cursor.executemany("INSERT INTO Courses VALUES (?, ?);", [
    (1, "Python для начинающих"),
    (2, "Веб-разработка"),
    (3, "Машинное обучение"),
    (4, "Анализ данных"),
    (5, "SQL основы")
])

cursor.executemany("INSERT INTO Enrollments VALUES (?, ?, ?, ?);", [
    (1, 101, 1, "2024-05-01"),
    (2, 102, 1, "2024-05-02"),
    (3, 103, 2, "2024-05-03"),
    (4, 104, 3, "2024-05-04")
])

conn.commit()

# SQL-запрос: курсы без регистраций
print("Курсы, на которые никто не зарегистрировался:\n")
cursor.execute("""
SELECT c.course_id, c.course_title
FROM Courses c
LEFT JOIN Enrollments e ON c.course_id = e.course_id
WHERE e.course_id IS NULL;
""")

for row in cursor.fetchall():
    print(row)

conn.close()
print("\nБаза данных сохранена как courses_enrollments.db")
