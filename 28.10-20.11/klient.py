import psycopg2

connection = psycopg2.connect(
    host="localhost",
    port="5432",
    database="my_python_app",
    user="postgres",
    password="khadimov"  # замени на свой пароль
)

cursor = connection.cursor()

# Создаём таблицы
cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id SERIAL PRIMARY KEY,
        name TEXT
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        client_id INT REFERENCES clients(id)
    );
""")

# Чистим данные
cursor.execute("DELETE FROM orders;")
cursor.execute("DELETE FROM clients;")

# Добавляем клиентов
cursor.execute("INSERT INTO clients (name) VALUES (%s)", ('Alice',))
cursor.execute("INSERT INTO clients (name) VALUES (%s)", ('Bob',))
cursor.execute("INSERT INTO clients (name) VALUES (%s)", ('Charlie',))

# Добавляем заказы
cursor.execute("INSERT INTO orders (client_id) VALUES (%s)", (1,))
cursor.execute("INSERT INTO orders (client_id) VALUES (%s)", (1,))
cursor.execute("INSERT INTO orders (client_id) VALUES (%s)", (2,))
cursor.execute("INSERT INTO orders (client_id) VALUES (%s)", (3,))
cursor.execute("INSERT INTO orders (client_id) VALUES (%s)", (3,))
cursor.execute("INSERT INTO orders (client_id) VALUES (%s)", (3,))

connection.commit()

# Запрос: количество заказов по каждому клиенту
cursor.execute("""
    SELECT c.name, COUNT(o.id) AS orders_count
    FROM clients c
    LEFT JOIN orders o ON c.id = o.client_id
    GROUP BY c.id, c.name
    ORDER BY orders_count DESC;
""")

rows = cursor.fetchall()

print("Количество заказов по клиентам:")
for row in rows:
    print(row)

cursor.close()
connection.close()
