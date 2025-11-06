import sqlite3

# Создаём или подключаем базу
conn = sqlite3.connect('customers.db')
cursor = conn.cursor()

# Удаляем старые таблицы, если есть
cursor.execute('DROP TABLE IF EXISTS Customers2024')
cursor.execute('DROP TABLE IF EXISTS Customers2025')

# Создаём таблицы
cursor.execute('''
CREATE TABLE Customers2024 (
    CustomerID INTEGER PRIMARY KEY,
    CustomerName TEXT
)
''')

cursor.execute('''
CREATE TABLE Customers2025 (
    CustomerID INTEGER PRIMARY KEY,
    CustomerName TEXT
)
''')

# Добавляем данные (пример)
cursor.executemany('INSERT INTO Customers2024 (CustomerID, CustomerName) VALUES (?, ?)', [
    (1, 'Alice'),
    (2, 'Bob'),
    (3, 'Charlie'),
    (4, 'Diana')
])

cursor.executemany('INSERT INTO Customers2025 (CustomerID, CustomerName) VALUES (?, ?)', [
    (2, 'Bob'),
    (3, 'Charlie'),
    (5, 'Eve'),
    (6, 'Frank')
])

# 1. Клиенты, которые были в 2024, но не попали в 2025
cursor.execute('''
SELECT CustomerName
FROM Customers2024
EXCEPT
SELECT CustomerName
FROM Customers2025
''')
old_only = cursor.fetchall()

# 2. Клиенты, которые появились только в 2025
cursor.execute('''
SELECT CustomerName
FROM Customers2025
EXCEPT
SELECT CustomerName
FROM Customers2024
''')
new_only = cursor.fetchall()

# Вывод результатов
print("Клиенты, которые были в 2024, но не в 2025:")
for row in old_only:
    print("-", row[0])

print("\nКлиенты, которые появились только в 2025:")
for row in new_only:
    print("-", row[0])

# Сохраняем и закрываем соединение
conn.commit()
conn.close()

print("\nБаза данных сохранена в файле customers.db")
