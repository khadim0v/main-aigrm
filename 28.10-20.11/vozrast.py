import psycopg2

connection = psycopg2.connect(
    host="localhost",
    port="5432",
    database="my_python_app",
    user="postgres",
    password="khadimov"  # замените своим
)

cursor = connection.cursor()

# Создаем таблицу departments
cursor.execute("""
    CREATE TABLE IF NOT EXISTS departments (
        id SERIAL PRIMARY KEY,
        name TEXT
    );
""")

# Создаем таблицу employees
cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id SERIAL PRIMARY KEY,
        name TEXT,
        age INT,
        department_id INT REFERENCES departments(id)
    );
""")

# Чистим данные
cursor.execute("DELETE FROM employees;")
cursor.execute("DELETE FROM departments;")

# Добавляем отделы
cursor.execute("INSERT INTO departments (name) VALUES (%s)", ('IT',))
cursor.execute("INSERT INTO departments (name) VALUES (%s)", ('HR',))
cursor.execute("INSERT INTO departments (name) VALUES (%s)", ('Finance',))

# Добавляем сотрудников
cursor.execute("INSERT INTO employees (name, age, department_id) VALUES (%s, %s, %s)", ('Alice', 25, 1))
cursor.execute("INSERT INTO employees (name, age, department_id) VALUES (%s, %s, %s)", ('Bob', 30, 1))
cursor.execute("INSERT INTO employees (name, age, department_id) VALUES (%s, %s, %s)", ('Charlie', 41, 2))
cursor.execute("INSERT INTO employees (name, age, department_id) VALUES (%s, %s, %s)", ('Diana', 29, 2))
cursor.execute("INSERT INTO employees (name, age, department_id) VALUES (%s, %s, %s)", ('Edward', 35, 3))

connection.commit()

# Запрос — средний возраст сотрудников по отделам
cursor.execute("""
    SELECT d.name AS department, AVG(e.age) AS average_age
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    GROUP BY d.name;
""")

rows = cursor.fetchall()

print("Средний возраст сотрудников по отделам:")
for row in rows:
    print(row)

cursor.close()
connection.close()
