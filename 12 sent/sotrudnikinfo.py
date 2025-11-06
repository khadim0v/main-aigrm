import sqlite3
import os

# Удаляем старую базу, если она уже есть
if os.path.exists("employees_projects.db"):
    os.remove("employees_projects.db")

# Подключаемся к SQLite
conn = sqlite3.connect("employees_projects.db")
cursor = conn.cursor()

# Создаем таблицы
cursor.executescript("""
CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    employee_name TEXT,
    department TEXT
);

CREATE TABLE projects (
    project_id INTEGER PRIMARY KEY,
    project_name TEXT,
    employee_id INTEGER,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);
""")

# Добавляем данные
cursor.executemany("INSERT INTO employees VALUES (?, ?, ?);", [
    (1, "Иванов", "Отдел продаж"),
    (2, "Петров", "Маркетинг"),
    (3, "Сидоров", "IT"),
    (4, "Ким", "Финансы"),
    (5, "Анна", "IT")
])

cursor.executemany("INSERT INTO projects VALUES (?, ?, ?);", [
    (1, "Проект A", 1),
    (2, "Проект B", 3),
    (3, "Проект C", None),
    (4, "Проект D", 5)
])

conn.commit()

# 1. Все сотрудники + проекты (LEFT JOIN)
print("1. Все сотрудники и проекты (включая тех, у кого нет проектов):")
cursor.execute("""
SELECT e.employee_name, e.department, p.project_name
FROM employees e
LEFT JOIN projects p ON e.employee_id = p.employee_id;
""")
for row in cursor.fetchall():
    print(row)

# 2. Все проекты + сотрудники (RIGHT JOIN через симуляцию)
print("\n2. Все проекты и сотрудники (включая проекты без сотрудников):")
cursor.execute("""
SELECT p.project_name, e.employee_name, e.department
FROM projects p
LEFT JOIN employees e ON p.employee_id = e.employee_id;
""")
for row in cursor.fetchall():
    print(row)

# 3. Сотрудники без проектов
print("\n3. Сотрудники, не участвующие ни в одном проекте:")
cursor.execute("""
SELECT e.employee_name, e.department
FROM employees e
LEFT JOIN projects p ON e.employee_id = p.employee_id
WHERE p.project_id IS NULL;
""")
for row in cursor.fetchall():
    print(row)

# 4. Полный OUTER JOIN (все сотрудники + все проекты)
print("\n4. Полный список сотрудников и проектов (FULL OUTER JOIN):")
cursor.execute("""
SELECT e.employee_name, e.department, p.project_name
FROM employees e
LEFT JOIN projects p ON e.employee_id = p.employee_id
UNION
SELECT e.employee_name, e.department, p.project_name
FROM projects p
LEFT JOIN employees e ON p.employee_id = e.employee_id;
""")
for row in cursor.fetchall():
    print(row)

conn.close()
print("\nБаза данных сохранена как employees_projects.db")
