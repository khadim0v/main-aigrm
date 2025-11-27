# fetch_problem_orders_example.py
import psycopg2
from psycopg2 import DatabaseError

DSN = {
    'host': 'localhost',
    'port': 5432,
    'database': 'my_python_app',  # замени на свою базу
    'user': 'postgres',
    'password': 'khadimov'
}

def setup_orders_table(conn):
    with conn.cursor() as cur:
        # Удаляем старое (если есть) вместе с зависимостями
        cur.execute("DROP TABLE IF EXISTS orders CASCADE;")
        # Создаём таблицу заново
        cur.execute("""
            CREATE TABLE orders (
                id SERIAL PRIMARY KEY,
                status TEXT NOT NULL,
                total_amount NUMERIC NOT NULL
            );
        """)
        # Вставляем тестовые данные
        cur.execute("""
            INSERT INTO orders (status, total_amount) VALUES
            ('new', 100),
            ('Cancelled', 200),
            ('processing', 50),
            ('new', -10),
            ('shipped', 0);
        """)
    conn.commit()
    print("Orders table created and test data inserted.")


def fetch_problem_orders(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, status, total_amount
            FROM orders
            WHERE total_amount <= 0 OR status = 'Cancelled'
            ORDER BY id;
        """)
        rows = cur.fetchall()
        if not rows:
            print("No problematic orders found.")
        else:
            print("Problematic orders:")
            for r in rows:
                print(f"ID={r[0]}, Status={r[1]}, Total={r[2]}")

def main():
    try:
        conn = psycopg2.connect(**DSN)
    except psycopg2.OperationalError as e:
        print("Connection failed:", e)
        return

    try:
        setup_orders_table(conn)
        fetch_problem_orders(conn)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
