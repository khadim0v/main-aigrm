import sqlite3

# Создаём базу данных
conn = sqlite3.connect("products.db")
cursor = conn.cursor()

# Удаляем таблицу, если уже существует
cursor.execute("DROP TABLE IF EXISTS Products")

# Создаём таблицу товаров
cursor.execute("""
CREATE TABLE Products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    price REAL,
    discount_price REAL
)
""")

# Добавляем тестовые данные
products_data = [
    (1, "Ноутбук", 120000, 100000),
    (2, "Телефон", 80000, 80000),
    (3, "Наушники", 15000, 12000),
    (4, "Монитор", 50000, 50000),
    (5, "Мышь", 10000, 8500)
]
cursor.executemany("INSERT INTO Products VALUES (?, ?, ?, ?)", products_data)

# SQL-запрос с IIF
cursor.execute("""
SELECT 
    name,
    IIF(price != discount_price, 'Есть скидка', 'Без скидки') AS discount_status
FROM Products
""")

# Вывод результата
print("Проверка наличия скидок:")
for name, status in cursor.fetchall():
    print(f"{name}: {status}")

# Сохраняем изменения и закрываем
conn.commit()
conn.close()

print("\nБаза данных сохранена в products.db")
