import psycopg2

connection = psycopg2.connect(
    host="localhost",
    port="5432",
    database="my_python_app",
    user="postgres",
    password="khadimov"  # замените своим
)

cursor = connection.cursor()

# Создаем таблицы
cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees_office1 (
        id SERIAL PRIMARY KEY,
        name TEXT,
        position TEXT
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees_office2 (
        id SERIAL PRIMARY KEY,
        name TEXT,
        position TEXT
    );
""")

# Очищаем таблицы перед вставкой, чтобы не дублировать данные
cursor.execute("DELETE FROM employees_office1;")
cursor.execute("DELETE FROM employees_office2;")

# Вставляем данные в офис 1
cursor.execute("INSERT INTO employees_office1 (name, position) VALUES (%s, %s)", ('Alice', 'Manager'))
cursor.execute("INSERT INTO employees_office1 (name, position) VALUES (%s, %s)", ('Bob', 'Developer'))
cursor.execute("INSERT INTO employees_office1 (name, position) VALUES (%s, %s)", ('Charlie', 'Designer'))

# Вставляем данные в офис 2
cursor.execute("INSERT INTO employees_office2 (name, position) VALUES (%s, %s)", ('David', 'Developer'))
cursor.execute("INSERT INTO employees_office2 (name, position) VALUES (%s, %s)", ('Eva', 'Manager'))
cursor.execute("INSERT INTO employees_office2 (name, position) VALUES (%s, %s)", ('Frank', 'Tester'))

connection.commit()

# Выполняем запрос: сотрудники с одинаковыми должностями в обоих офисах
cursor.execute("""
    SELECT o1.name, o1.position
    FROM employees_office1 o1
    JOIN employees_office2 o2
    ON o1.position = o2.position;
""")

rows = cursor.fetchall()

print("Сотрудники с одинаковыми должностями в двух офисах:")
for row in rows:
    print(row)

cursor.close()
connection.close()
