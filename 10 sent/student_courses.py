import sqlite3
import os

# Удаляем старую базу, если она уже есть
if os.path.exists("students_courses.db"):
    os.remove("students_courses.db")

# Подключаемся к базе данных
conn = sqlite3.connect("students_courses.db")
cursor = conn.cursor()

# Создаем таблицу Students
cursor.execute('''
CREATE TABLE Students (
    StudentID INTEGER PRIMARY KEY,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL
);
''')

# Создаем таблицу Courses
cursor.execute('''
CREATE TABLE Courses (
    CourseID INTEGER PRIMARY KEY,
    CourseName TEXT NOT NULL
);
''')

# Создаем таблицу Enrollments (связь студентов и курсов)
cursor.execute('''
CREATE TABLE Enrollments (
    EnrollmentID INTEGER PRIMARY KEY,
    StudentID INTEGER,
    CourseID INTEGER,
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
    FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
);
''')

# Заполняем таблицу Students
cursor.executemany('''
INSERT INTO Students (StudentID, FirstName, LastName)
VALUES (?, ?, ?);
''', [
    (1, 'Андрей', 'Иванов'),
    (2, 'Мария', 'Петрова'),
    (3, 'Илья', 'Ильин'),
    (4, 'Ольга', 'Сидорова'),
    (5, 'Инна', 'Игнатьева')
])

# Заполняем таблицу Courses
cursor.executemany('''
INSERT INTO Courses (CourseID, CourseName)
VALUES (?, ?);
''', [
    (1, 'Математика'),
    (2, 'Информатика'),
    (3, 'Физика')
])

# Заполняем таблицу Enrollments
cursor.executemany('''
INSERT INTO Enrollments (EnrollmentID, StudentID, CourseID)
VALUES (?, ?, ?);
''', [
    (1, 1, 1),
    (2, 1, 2),
    (3, 2, 3),
    (4, 3, 2),
    (5, 4, 1),
    (6, 5, 2)
])

conn.commit()

# Выполняем INNER JOIN и фильтрацию по фамилии
print("Студенты, чья фамилия начинается с 'И':\n")
cursor.execute('''
SELECT s.StudentID, s.FirstName, s.LastName, c.CourseName
FROM Students s
INNER JOIN Enrollments e ON s.StudentID = e.StudentID
INNER JOIN Courses c ON e.CourseID = c.CourseID
WHERE s.LastName LIKE 'И%';
''')

rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
print("\nБаза данных успешно создана и сохранена как students_courses.db")
