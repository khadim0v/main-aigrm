import psycopg2

connection = psycopg2.connect(
    host="localhost",
    port="5432",
    database="my_python_app",
    user="postgres",
    password="khadimov"  # замените своим
)

cursor = connection.cursor()

# Создаём таблицу
cursor.execute("""
    CREATE TABLE IF NOT EXISTS cars (
        id SERIAL PRIMARY KEY,
        brand VARCHAR(50),
        model VARCHAR(50),
        color VARCHAR(20) DEFAULT 'не указан'
    );
""")

# Чистим таблицу для демонстрации
cursor.execute("DELETE FROM cars;")

# Добавляем запись без цвета — DEFAULT сработает автоматически
cursor.execute("""
    INSERT INTO cars (brand, model)
    VALUES (%s, %s);
""", ('Toyota', 'Camry'))

connection.commit()

# Проверяем данные
cursor.execute("SELECT * FROM cars;")
rows = cursor.fetchall()

print("Содержимое таблицы cars:")
for row in rows:
    print(row)

cursor.close()
connection.close()
