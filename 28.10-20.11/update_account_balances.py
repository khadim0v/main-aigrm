# update_account_balances_full.py
import psycopg2
from psycopg2 import sql

DSN = {
    'host': 'localhost',
    'port': 5432,
    'database': 'my_python_app',  # твоя база
    'user': 'postgres',
    'password': 'khadimov'
}

def setup_tables(conn):
    with conn.cursor() as cur:
        # создаём таблицу accounts, если нет
        cur.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            balance NUMERIC DEFAULT 0
        );
        """)
        # создаём таблицу transactions, если нет
        cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            acc_id INT REFERENCES accounts(id) ON DELETE CASCADE,
            amount NUMERIC NOT NULL
        );
        """)
        # добавим тестовые данные, если таблицы пустые
        cur.execute("SELECT COUNT(*) FROM accounts;")
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO accounts (balance) VALUES (100), (200), (300);")
        cur.execute("SELECT COUNT(*) FROM transactions;")
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO transactions (acc_id, amount) VALUES (1,50),(1,25),(2,100),(3,75),(3,25);")
    conn.commit()
    print("Tables and test data ready.")

def update_balances(conn):
    with conn.cursor() as cur:
        cur.execute("""
        UPDATE accounts a
        SET balance = a.balance + t.total_amount
        FROM (
            SELECT acc_id, SUM(amount) AS total_amount
            FROM transactions
            GROUP BY acc_id
        ) t
        WHERE a.id = t.acc_id;
        """)
    conn.commit()
    print("Balances updated.")

def report_accounts(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id, balance FROM accounts ORDER BY id;")
        rows = cur.fetchall()
        print("Accounts:")
        for row in rows:
            print(f"ID={row[0]}, Balance={row[1]}")

def main():
    try:
        conn = psycopg2.connect(**DSN)
    except psycopg2.OperationalError as e:
        print("Connection failed:", e)
        return

    try:
        setup_tables(conn)
        report_accounts(conn)
        update_balances(conn)
        report_accounts(conn)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
