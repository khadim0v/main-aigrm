import sqlite3

# Создаём базу данных в памяти
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Создаём таблицы
cursor.execute('''
CREATE TABLE Customers (
    CustomerID INTEGER PRIMARY KEY,
    Name TEXT,
    City TEXT,
    Country TEXT
)
''')

cursor.execute('''
CREATE TABLE Employees (
    EmployeeID INTEGER PRIMARY KEY,
    Name TEXT,
    City TEXT,
    Country TEXT
)
''')

# Добавляем примерные данные
cursor.executemany('INSERT INTO Customers (Name, City, Country) VALUES (?, ?, ?)', [
    ('Anna Schmidt', 'Berlin', 'Germany'),
    ('Pierre Dupont', 'Paris', 'France'),
    ('John Doe', 'London', 'UK'),
])

cursor.executemany('INSERT INTO Employees (Name, City, Country) VALUES (?, ?, ?)', [
    ('Hans Müller', 'Munich', 'Germany'),
    ('Marie Curie', 'Paris', 'France'),
    ('James Smith', 'New York', 'USA'),
])

# Выполняем объединённый запрос
query = '''
SELECT 
    Name,
    City,
    Country,
    'Customer' AS Role
FROM Customers
WHERE Country IN ('Germany', 'France')

UNION ALL

SELECT 
    Name,
    City,
    Country,
    'Employee' AS Role
FROM Employees
WHERE Country IN ('Germany', 'France')

ORDER BY City, Name
'''

cursor.execute(query)
results = cursor.fetchall()

# Выводим результат
print("Name | City | Country | Role")
print("-" * 40)
for row in results:
    print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")

conn.close()
