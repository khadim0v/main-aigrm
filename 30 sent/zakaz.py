import sqlite3

# Создание базы данных
conn = sqlite3.connect('orders.db')
cursor = conn.cursor()

# Удаляем таблицу, если существует
cursor.execute('DROP TABLE IF EXISTS Orders')

# Создаём таблицу
cursor.execute('''
CREATE TABLE Orders (
    order_id INTEGER PRIMARY KEY,
    status_Xcode INTEGER
)
''')

# Добавляем тестовые данные
orders_data = [
    (1, 0),
    (2, 1),
    (3, 2),
    (4, 3),
    (5, 7)
]
cursor.executemany('INSERT INTO Orders VALUES (?, ?)', orders_data)

# SQL-запрос с CASE
cursor.execute('''
SELECT 
    order_id,
    CASE status_Xcode
        WHEN 0 THEN 'Новый'
        WHEN 1 THEN 'В обработке'
        WHEN 2 THEN 'Отгружен'
        WHEN 3 THEN 'Доставлен'
        ELSE 'Неизвестно'
    END AS status_text
FROM Orders
''')

# Вывод результата
print("Статусы заказов:")
for order_id, status in cursor.fetchall():
    print(f"Заказ {order_id}: {status}")

# Сохраняем и закрываем базу
conn.commit()
conn.close()

print("\nБаза данных сохранена в файле orders.db")
