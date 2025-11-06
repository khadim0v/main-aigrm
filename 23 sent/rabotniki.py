import sqlite3

# Создаём или подключаем базу данных
conn = sqlite3.connect('employees.db')
cursor = conn.cursor()

# Удаляем таблицы, если уже есть
cursor.execute('DROP TABLE IF EXISTS Employees')
cursor.execute('DROP TABLE IF EXISTS FormerEmployees')

# Создаём таблицы
cursor.execute('''
CREATE TABLE Employees (
    EmployeeID INTEGER PRIMARY KEY,
    FullName TEXT,
    Department TEXT
)
''')

cursor.execute('''
CREATE TABLE FormerEmployees (
    EmployeeID INTEGER PRIMARY KEY,
    FullName TEXT,
    Department TEXT
)
''')

# Пример данных
cursor.executemany('INSERT INTO Employees VALUES (?, ?, ?)', [
    (1, 'Alice Brown', 'IT'),
    (2, 'Bob Smith', 'HR'),
    (3, 'Charlie Johnson', 'Finance'),
    (4, 'Diana Miller', 'Marketing')
])

cursor.executemany('INSERT INTO FormerEmployees VALUES (?, ?, ?)', [
    (3, 'Charlie Johnson', 'Finance'),
    (5, 'Eve Davis', 'IT'),
    (6, 'Frank Wilson', 'Sales')
])

# 1. Сотрудники, которые сейчас работают, но никогда не были уволены
cursor.execute('''
SELECT FullName
FROM Employees
EXCEPT
SELECT FullName
FROM FormerEmployees
''')
still_working = cursor.fetchall()

# 2. Сотрудники, которые уволились, но не вернулись обратно
cursor.execute('''
SELECT FullName
FROM FormerEmployees
EXCEPT
SELECT FullName
FROM Employees
''')
former_only = cursor.fetchall()

# Вывод результатов
print("Сотрудники, которые работают, но не были уволены:")
for row in still_working:
    print("-", row[0])

print("\nСотрудники, которые уволились и не вернулись:")
for row in former_only:
    print("-", row[0])

# Сохраняем и закрываем базу
conn.commit()
conn.close()

print("\nБаза данных сохранена в файле employees.db")
