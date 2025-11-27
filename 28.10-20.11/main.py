import psycopg2

# Подключение к базе данных
connection = psycopg2.connect(
    host="localhost",
    port="5432",
    database="my_python_app",
    user="postgres",
    password="khadimov"  # замените на свой пароль
)

cursor = connection.cursor()

# 1. Создаем таблицу (если еще не существует)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT NOT NULL
    );
""")

# 2. Вставляем несколько пользователей
cursor.execute("INSERT INTO users (username) VALUES (%s)", ('Alice',))
cursor.execute("INSERT INTO users (username) VALUES (%s)", ('Bob',))
cursor.execute("INSERT INTO users (username) VALUES (%s)", ('Charlie',))

# Сохраняем изменения
connection.commit()

# 3. Получаем всех пользователей
cursor.execute("SELECT * FROM users;")
rows = cursor.fetchall()

print("Пользователи в базе данных:")
for row in rows:
    print(f"id={row[0]}, username={row[1]}")

# Закрываем соединение
cursor.close()
connection.close()
