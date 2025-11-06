#!/usr/bin/env python3
"""
Короткий Python-скрипт: создаёт SQLite БД интернет-магазина, заполняет данными
и выполняет запрошенные аналитические SQL-запросы, выводя результаты в терминал.
Скопируй в файл и запусти: python shop_analysis.py
"""
import sqlite3
from pathlib import Path

DB_PATH = "shop_analysis.db"

SCHEMA_AND_SEED = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at DATE DEFAULT (DATE('now'))
);

CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER REFERENCES categories(category_id),
    price NUMERIC(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL
);

-- Примеры данных
INSERT OR IGNORE INTO customers (customer_id, name, email, created_at) VALUES
  (1, 'Alice', 'alice@example.com', '2022-11-10'),
  (2, 'Bob', 'bob@example.com', '2023-02-01'),
  (3, 'Carol', 'carol@example.com', '2021-07-15'),
  (4, 'Dave', 'dave@example.com', '2024-01-20');

INSERT OR IGNORE INTO categories (category_id, name) VALUES
  (1, 'Electronics'),
  (2, 'Books'),
  (3, 'Clothing');

INSERT OR IGNORE INTO products (product_id, name, category_id, price) VALUES
  (1, 'Smartphone', 1, 699.99),
  (2, 'Laptop', 1, 1299.00),
  (3, 'Novel A', 2, 19.90),
  (4, 'Novel B', 2, 25.50),
  (5, 'T-Shirt', 3, 15.00);

INSERT OR IGNORE INTO orders (order_id, customer_id, order_date) VALUES
  (1, 1, '2022-12-20'),
  (2, 2, '2023-05-10'),
  (3, 2, '2024-02-15'),
  (4, 3, '2023-03-01'),
  (5, 4, '2024-09-01');

INSERT OR IGNORE INTO order_items (order_item_id, order_id, product_id, quantity, unit_price) VALUES
  (1, 1, 3, 2, 19.90),
  (2, 2, 1, 1, 699.99),
  (3, 2, 4, 1, 25.50),
  (4, 3, 2, 1, 1299.00),
  (5, 3, 5, 3, 15.00),
  (6, 4, 3, 1, 19.90),
  (7, 5, 1, 2, 699.99),
  (8, 5, 5, 1, 15.00);
"""

QUERIES = [
    {
        "title": "1) Клиенты, которые сделали заказы после 2023-01-01",
        "sql": """
            SELECT DISTINCT c.customer_id, c.name, c.email
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            WHERE o.order_date > DATE('2023-01-01')
            ORDER BY c.customer_id;
        """,
    },
    {
        "title": "2) Сколько товаров продано по каждой категории (сумма quantity)",
        "sql": """
            SELECT
              cat.category_id,
              cat.name AS category,
              COALESCE(SUM(oi.quantity), 0) AS total_items_sold
            FROM categories cat
            LEFT JOIN products p ON p.category_id = cat.category_id
            LEFT JOIN order_items oi ON oi.product_id = p.product_id
            GROUP BY cat.category_id, cat.name
            ORDER BY total_items_sold DESC;
        """,
    },
    {
        "title": "3) Топ-3 самых дорогих товаров",
        "sql": """
            SELECT product_id, name, price
            FROM products
            ORDER BY price DESC
            LIMIT 3;
        """,
    },
    {
        "title": "4) Список заказов с общей суммой (unit_price * quantity) для каждого заказа",
        "sql": """
            SELECT
              o.order_id,
              o.customer_id,
              o.order_date,
              ROUND(SUM(oi.quantity * oi.unit_price), 2) AS order_total
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY o.order_id, o.customer_id, o.order_date
            ORDER BY order_total DESC;
        """,
    },
    {
        "title": "5) Клиент, который потратил больше всего денег",
        "sql": """
            SELECT
              c.customer_id,
              c.name,
              c.email,
              ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_spent
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY c.customer_id, c.name, c.email
            ORDER BY total_spent DESC
            LIMIT 1;
        """,
    },
]

def execute_script(conn, script: str):
    cur = conn.cursor()
    cur.executescript(script)
    conn.commit()

def run_and_print(conn, title: str, sql: str):
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description] if cur.description else []
    print("\n" + title)
    print("-" * len(title))
    if not rows:
        print(" (нет результатов)")
        return
    # печать заголовка таблицы
    print(" | ".join(cols))
    print("-" * (len(" | ".join(cols)) + 5))
    for row in rows:
        print(" | ".join(str(r) for r in row))

def main():
    # создать файл БД, если ещё нет
    db_file = Path(DB_PATH)
    first_time = not db_file.exists()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # можно обращаться по именам, но печатаем кортежи
    if first_time:
        execute_script(conn, SCHEMA_AND_SEED)
    else:
        # на всякий случай убедимся, что таблицы существуют и seed применён idempotent
        execute_script(conn, "BEGIN; " + SCHEMA_AND_SEED + " COMMIT;")
    # выполнить запросы
    for q in QUERIES:
        run_and_print(conn, q["title"], q["sql"])
    conn.close()

if __name__ == "__main__":
    main()
