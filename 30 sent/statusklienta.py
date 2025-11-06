import sqlite3
from datetime import datetime, timedelta

# Создание и подключение базы данных
conn = sqlite3.connect("clients.db")
cursor = conn.cursor()

# Удаляем таблицу, если существует
cursor.execute("DROP TABLE IF EXISTS Clients")

# Создаём таблицу
cursor.execute("""
CREATE TABLE Clients (
    id INTEGER PRIMARY KEY,
    name TEXT,
    last_purchase_date DATE,
    total_spent REAL
)
""")

# Добавляем тестовые данные
today = datetime.today().date()
clients_data = [
    (1, "Иван", today - timedelta(days=30), 60000),    # VIP
    (2, "Мария", today - timedelta(days=200), 20000),  # Удержание
    (3, "Петр", today - timedelta(days=90), 40000),    # Обычный
    (4, "Анна", today - timedelta(days=10), 45000),    # Обычный
    (5, "Сергей", today - timedelta(days=45), 80000)   # VIP
]
cursor.executemany("INSERT INTO Clients VALUES (?, ?, ?, ?)", clients_data)

# SQL-запрос с CASE
cursor.execute(f"""
SELECT 
    name,
    CASE
        WHEN total_spent > 50000 AND julianday('now') - julianday(last_purchase_date) <= 60 THEN 'VIP'
        WHEN julianday('now') - julianday(last_purchase_date) > 180 THEN 'Удержание'
        ELSE 'Обычный'
    END AS client_status
FROM Clients
""")

# Вывод результата
print("Статусы клиентов:")
for name, status in cursor.fetchall():
    print(f"{name}: {status}")

# Сохраняем изменения
conn.commit()
conn.close()

print("\nБаза данных сохранена в clients.db")
