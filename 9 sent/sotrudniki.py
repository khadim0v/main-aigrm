import sqlite3
import os

# Удаляем старую базу, если она уже есть
if os.path.exists("company.db"):
    os.remove("company.db")

# Создаем подключение к файлу базы данных
conn = sqlite3.connect("company.db")
cursor = conn.cursor()

# Создаем таблицу Departments
cursor.execute('''
CREATE TABLE Departments (
    DepartmentID INTEGER PRIMARY KEY,
    DepartmentName TEXT NOT NULL,
    ManagerID INTEGER
);
''')

# Создаем таблицу Employees
cursor.execute('''
CREATE TABLE Employees (
    EmployeeID INTEGER PRIMARY KEY,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    DepartmentID INTEGER,
    FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID)
);
''')

# Заполняем таблицу Departments
cursor.executemany('''
INSERT INTO Departments (DepartmentID, DepartmentName, ManagerID)
VALUES (?, ?, ?);
''', [
    (1, 'IT', 101),
    (2, 'HR', 102),
    (3, 'Marketing', 103)
])

# Заполняем таблицу Employees (один без отдела)
cursor.executemany('''
INSERT INTO Employees (EmployeeID, FirstName, LastName, DepartmentID)
VALUES (?, ?, ?, ?);
''', [
    (1, 'Иван', 'Иванов', 1),
    (2, 'Анна', 'Смирнова', 2),
    (3, 'Петр', 'Кузнецов', 3),
    (4, 'Ольга', 'Васильева', None),
    (5, 'Дмитрий', 'Соколов', 1)
])

# Сохраняем изменения
conn.commit()

# INNER JOIN — только сотрудники с существующим отделом
print("Результат INNER JOIN (только с отделом):")
cursor.execute('''
SELECT e.EmployeeID, e.FirstName, e.LastName, d.DepartmentName
FROM Employees e
INNER JOIN Departments d
  ON e.DepartmentID = d.DepartmentID;
''')
for row in cursor.fetchall():
    print(row)

# LEFT JOIN — чтобы увидеть всех сотрудников, включая тех без отдела
print("\nРезультат LEFT JOIN (все сотрудники):")
cursor.execute('''
SELECT e.EmployeeID, e.FirstName, e.LastName, 
       COALESCE(d.DepartmentName, 'Не указан') AS DepartmentName
FROM Employees e
LEFT JOIN Departments d
  ON e.DepartmentID = d.DepartmentID;
''')
for row in cursor.fetchall():
    print(row)

conn.close()
print("\nБаза данных успешно сохранена как company.db")
