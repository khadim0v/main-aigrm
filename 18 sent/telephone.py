import sqlite3

# Подключаемся к базе (создаст файл, если его нет)
conn = sqlite3.connect('people.db')
cursor = conn.cursor()

# Создаем таблицы
cursor.execute('DROP TABLE IF EXISTS Customers')
cursor.execute('DROP TABLE IF EXISTS Employees')
cursor.execute('DROP TABLE IF EXISTS Suppliers')

cursor.execute('''
CREATE TABLE Customers (
    Name TEXT,
    Phone TEXT
)
''')

cursor.execute('''
CREATE TABLE Employees (
    Name TEXT,
    Phone TEXT
)
''')

cursor.execute('''
CREATE TABLE Suppliers (
    Name TEXT,
    Phone TEXT
)
''')

# Добавляем данные (некоторые телефоны NULL)
cursor.executemany('INSERT INTO Customers (Name, Phone) VALUES (?, ?)', [
    ('Anna Schmidt', '+49 123 456'),
    ('John Doe', None),
    ('Pierre Dupont', '+33 987 654')
])

cursor.executemany('INSERT INTO Employees (Name, Phone) VALUES (?, ?)', [
    ('Hans Müller', None),
    ('John Doe', '+44 222 111'),
    ('Maria Ivanova', '+7 777 555')
])

cursor.executemany('INSERT INTO Suppliers (Name, Phone) VALUES (?, ?)', [
    ('Pierre Dupont', '+33 987 654'),
    ('Tech Corp', None),
    ('Anna Schmidt', '+49 123 456')
])

# SQL-запрос для объединения данных без дублей
query = '''
SELECT DISTINCT
    Name,
    COALESCE(Phone, 'Номер не указан') AS Phone
FROM (
    SELECT Name, Phone FROM Customers
    UNION ALL
    SELECT Name, Phone FROM Employees
    UNION ALL
    SELECT Name, Phone FROM Suppliers
)
ORDER BY Name
'''

cursor.execute(query)
results = cursor.fetchall()

# Выводим результат
print("Name | Phone")
print("-" * 30)
for row in results:
    print(f"{row[0]} | {row[1]}")

# Сохраняем изменения
conn.commit()
conn.close()

print("\nДанные сохранены в базе people.db")
