import sqlite3

# Создание базы данных
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Удаляем таблицы, если уже есть
cursor.execute('DROP TABLE IF EXISTS WebUsers')
cursor.execute('DROP TABLE IF EXISTS AppUsers')

# Создаём таблицы
cursor.execute('''
CREATE TABLE WebUsers (
    UserID INTEGER PRIMARY KEY,
    UserName TEXT
)
''')

cursor.execute('''
CREATE TABLE AppUsers (
    UserID INTEGER PRIMARY KEY,
    UserName TEXT
)
''')

# Добавляем тестовые данные
cursor.executemany('INSERT INTO WebUsers VALUES (?, ?)', [
    (1, 'Alice'),
    (2, 'Bob'),
    (3, 'Charlie'),
    (4, 'Diana')
])

cursor.executemany('INSERT INTO AppUsers VALUES (?, ?)', [
    (3, 'Charlie'),
    (4, 'Diana'),
    (5, 'Eve'),
    (6, 'Frank')
])

# SQL-запрос: пользователи, которые есть и в сайте, и в приложении
cursor.execute('''
SELECT UserName
FROM WebUsers
INTERSECT
SELECT UserName
FROM AppUsers
''')

both_users = cursor.fetchall()

# Вывод результата
print("Пользователи, которые пользуются и сайтом, и приложением:")
for row in both_users:
    print("-", row[0])

# Сохраняем базу
conn.commit()
conn.close()

print("\nБаза данных сохранена в файле users.db")
