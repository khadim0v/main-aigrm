import random
import psycopg2
from psycopg2 import DatabaseError

DSN = {
    'host': 'localhost',
    'port': 5432,
    'database': 'my_python_app',
    'user': 'postgres',
    'password': 'khadimov'  # поменяй на свой пароль
}

def main():
    conn = psycopg2.connect(**DSN)
    try:
        cur = conn.cursor()

        # --- 1) Создаем схему, функции и триггер ---
        cur.execute("""
        -- Удаляем старое
        DROP TABLE IF EXISTS movements CASCADE;
        DROP TABLE IF EXISTS order_items CASCADE;
        DROP TABLE IF EXISTS orders CASCADE;
        DROP TABLE IF EXISTS inventory CASCADE;
        DROP TABLE IF EXISTS products CASCADE;
        DROP TABLE IF EXISTS warehouses CASCADE;
        DROP TABLE IF EXISTS customers CASCADE;

        -- Склады
        CREATE TABLE warehouses (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            city TEXT,
            capacity NUMERIC NOT NULL CHECK (capacity > 0)
        );

        -- Товары
        CREATE TABLE products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            price NUMERIC(12,2) NOT NULL CHECK (price >= 0),
            unit_volume NUMERIC NOT NULL CHECK (unit_volume > 0)
        );

        -- Остатки
        CREATE TABLE inventory (
            warehouse_id INT NOT NULL REFERENCES warehouses(id) ON DELETE CASCADE,
            product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            quantity INT NOT NULL CHECK (quantity >= 0),
            PRIMARY KEY (warehouse_id, product_id)
        );

        -- Клиенты
        CREATE TABLE customers (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL
        );

        -- Заказы
        CREATE TABLE orders (
            id SERIAL PRIMARY KEY,
            customer_id INT REFERENCES customers(id) ON DELETE SET NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            status TEXT NOT NULL CHECK (status IN ('new','processing','shipped','cancelled')),
            total_amount NUMERIC(14,2) DEFAULT 0 NOT NULL CHECK (total_amount >= 0),
            allocated_warehouse_id INT REFERENCES warehouses(id) ON DELETE SET NULL
        );

        -- Позиции заказа
        CREATE TABLE order_items (
            id SERIAL PRIMARY KEY,
            order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
            product_id INT NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
            quantity INT NOT NULL CHECK (quantity > 0)
        );

        -- Журнал движения
        CREATE TABLE movements (
            id SERIAL PRIMARY KEY,
            warehouse_id INT REFERENCES warehouses(id) ON DELETE SET NULL,
            product_id INT REFERENCES products(id) ON DELETE SET NULL,
            quantity_change INT NOT NULL,
            reason TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        );

        -- Функция безопасного поступления
        CREATE OR REPLACE FUNCTION add_stock_safe(wh_id INT, prod_id INT, qty INT)
        RETURNS VOID LANGUAGE plpgsql AS $$
        DECLARE
            current_volume NUMERIC;
            incoming_volume NUMERIC;
            max_capacity NUMERIC;
            prod_volume NUMERIC;
        BEGIN
            IF qty <= 0 THEN RAISE EXCEPTION 'Quantity must be positive'; END IF;

            SELECT unit_volume INTO prod_volume FROM products WHERE id = prod_id;
            IF NOT FOUND THEN RAISE EXCEPTION 'Product % does not exist', prod_id; END IF;

            incoming_volume := prod_volume * qty;

            SELECT COALESCE(SUM(i.quantity * p.unit_volume),0)
            INTO current_volume
            FROM inventory i JOIN products p ON p.id = i.product_id
            WHERE i.warehouse_id = wh_id;

            SELECT capacity INTO max_capacity FROM warehouses WHERE id = wh_id;
            IF NOT FOUND THEN RAISE EXCEPTION 'Warehouse % does not exist', wh_id; END IF;

            IF current_volume + incoming_volume > max_capacity THEN
                RAISE EXCEPTION 'Not enough capacity on warehouse %: need % but have % free',
                    wh_id, (current_volume + incoming_volume) - max_capacity, max_capacity - current_volume;
            END IF;

            INSERT INTO inventory (warehouse_id, product_id, quantity)
            VALUES (wh_id, prod_id, qty)
            ON CONFLICT (warehouse_id, product_id)
            DO UPDATE SET quantity = inventory.quantity + EXCLUDED.quantity;

            INSERT INTO movements (warehouse_id, product_id, quantity_change, reason)
            VALUES (wh_id, prod_id, qty, 'add_stock_safe');

        END;
        $$;

        -- Функция allocate_order
        CREATE OR REPLACE FUNCTION allocate_order(o_id INT) RETURNS VOID LANGUAGE plpgsql AS $$
        DECLARE
            candidate_wh INT;
            required_items_count INT;
        BEGIN
            SELECT COUNT(*) INTO required_items_count FROM order_items WHERE order_id = o_id;
            IF required_items_count = 0 THEN
                UPDATE orders SET status='cancelled' WHERE id=o_id;
                RAISE EXCEPTION 'Order % has no items', o_id;
            END IF;

            WITH req AS (
                SELECT product_id, quantity AS req_qty FROM order_items WHERE order_id = o_id
            ),
            avail AS (
                SELECT i.warehouse_id, i.product_id, i.quantity AS avail_qty FROM inventory i
            ),
            matched AS (
                SELECT a.warehouse_id,
                       COUNT(*) FILTER (WHERE a.avail_qty >= r.req_qty) AS ok_count,
                       SUM(a.avail_qty) FILTER (WHERE a.product_id IN (SELECT product_id FROM req)) AS total_available_for_items
                FROM avail a
                JOIN req r ON r.product_id = a.product_id
                GROUP BY a.warehouse_id
            ),
            candidates AS (
                SELECT warehouse_id, ok_count, total_available_for_items
                FROM matched
                WHERE ok_count = (SELECT COUNT(*) FROM req)
            )
            SELECT warehouse_id INTO candidate_wh
            FROM candidates
            ORDER BY total_available_for_items DESC NULLS LAST
            LIMIT 1;

            IF candidate_wh IS NULL THEN
                UPDATE orders SET status='cancelled' WHERE id=o_id;
                RAISE EXCEPTION 'No single warehouse can fulfill order % — order cancelled', o_id;
            END IF;

            WITH req AS (
                SELECT product_id, quantity AS req_qty FROM order_items WHERE order_id = o_id
            )
            UPDATE inventory i
            SET quantity = i.quantity - r.req_qty
            FROM req r
            WHERE i.warehouse_id = candidate_wh AND i.product_id = r.product_id;

            INSERT INTO movements (warehouse_id, product_id, quantity_change, reason)
            SELECT candidate_wh, r.product_id, -r.quantity, 'allocate_order'
            FROM order_items r
            WHERE r.order_id = o_id;


            UPDATE orders SET status='processing', allocated_warehouse_id=candidate_wh WHERE id=o_id;

        END;
        $$;

        -- Триггер пересчёта total_amount
        CREATE OR REPLACE FUNCTION recalc_order_total() RETURNS TRIGGER LANGUAGE plpgsql AS $$
        DECLARE
            target_order INT;
            new_total NUMERIC := 0;
        BEGIN
            IF TG_OP = 'INSERT' THEN target_order := NEW.order_id;
            ELSIF TG_OP = 'UPDATE' THEN target_order := NEW.order_id;
            ELSIF TG_OP = 'DELETE' THEN target_order := OLD.order_id;
            ELSE RETURN NULL;
            END IF;

            SELECT COALESCE(SUM(oi.quantity*p.price),0) INTO new_total
            FROM order_items oi JOIN products p ON p.id=oi.product_id
            WHERE oi.order_id = target_order;

            UPDATE orders SET total_amount=new_total WHERE id=target_order;

            RETURN NULL;
        END;
        $$;

        CREATE TRIGGER trg_recalc_order_total
        AFTER INSERT OR UPDATE OR DELETE ON order_items
        FOR EACH ROW
        EXECUTE FUNCTION recalc_order_total();
        """)

        conn.commit()
        print("Schema, functions and triggers created successfully.")

        # --- 2) Начальные данные ---
        # Склады
        cur.execute("INSERT INTO warehouses (name, city, capacity) VALUES (%s,%s,%s) RETURNING id", ('WH_A','Almaty',5000))
        wh1 = cur.fetchone()[0]
        cur.execute("INSERT INTO warehouses (name, city, capacity) VALUES (%s,%s,%s) RETURNING id", ('WH_B','Astana',4000))
        wh2 = cur.fetchone()[0]
        cur.execute("INSERT INTO warehouses (name, city, capacity) VALUES (%s,%s,%s) RETURNING id", ('WH_C','Shymkent',6000))
        wh3 = cur.fetchone()[0]
        warehouses = [wh1, wh2, wh3]

        # Товары
        products = []
        for i in range(1, 11):
            name = f'Product_{i}'
            price = round(random.uniform(5,500),2)
            unit_volume = round(random.uniform(1,20),2)
            cur.execute("INSERT INTO products (name, price, unit_volume) VALUES (%s,%s,%s) RETURNING id", (name, price, unit_volume))
            pid = cur.fetchone()[0]
            products.append((pid, name, price, unit_volume))

        # Клиенты
        clients = []
        for name in ['Alice','Bob','Charlie','Diana']:
            cur.execute("INSERT INTO customers (name) VALUES (%s) RETURNING id", (name,))
            clients.append(cur.fetchone()[0])

        conn.commit()
        print("Initial warehouses, products, and clients inserted.")

        # --- 3) Распределяем начальные запасы ---
        for wh_id in warehouses:
            for pid, _, _, _ in products:
                qty = random.randint(5,20)
                try:
                    cur.execute("SELECT add_stock_safe(%s,%s,%s)", (wh_id, pid, qty))
                    conn.commit()
                except DatabaseError as e:
                    conn.rollback()
                    print(f"add_stock_safe failed for wh={wh_id} pid={pid} qty={qty}: {e}")

        # --- 4) Тест переполнения ---
        pid_test = products[0][0]
        try:
            cur.execute("SELECT add_stock_safe(%s,%s,%s)", (warehouses[0], pid_test, 100000))
            conn.commit()
            print("Unexpected: overfill succeeded.")
        except DatabaseError as e:
            conn.rollback()
            print("Expected error on overfill:", e)

        # --- 5) Создаем случайные заказы ---
        order_ids = []
        for _ in range(10):
            client_id = random.choice(clients)
            cur.execute("INSERT INTO orders (customer_id, status) VALUES (%s,'new') RETURNING id", (client_id,))
            oid = cur.fetchone()[0]
            k = random.randint(2,5)
            chosen = random.sample(products, k)
            for pid, _, _, _ in chosen:
                qty = random.randint(1,5)
                cur.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s,%s,%s)", (oid, pid, qty))
            order_ids.append(oid)
        conn.commit()

        # --- 6) Обрабатываем заказы ---
        for oid in order_ids:
            try:
                cur.execute("SELECT allocate_order(%s);", (oid,))
                conn.commit()
                cur.execute("SELECT allocated_warehouse_id, status FROM orders WHERE id=%s", (oid,))
                row = cur.fetchone()
                print(f"Order {oid} allocated to warehouse {row[0]}")
            except DatabaseError as e:
                conn.rollback()
                cur.execute("SELECT allocated_warehouse_id, status FROM orders WHERE id=%s", (oid,))
                row = cur.fetchone()
                print(f"Order {oid} failed: {e} (status now {row[1]})")

        # --- 7) Итоговые остатки ---
        print("\n--- Final stock per warehouse ---")
        cur.execute("""
            SELECT w.id, w.name, p.name, i.quantity
            FROM warehouses w
            JOIN inventory i ON i.warehouse_id=w.id
            JOIN products p ON p.id=i.product_id
            ORDER BY w.id, p.id
        """)
        for r in cur.fetchall():
            print(r)

        print("\n--- Orders summary ---")
        cur.execute("""
            SELECT o.id, c.name, o.status, o.allocated_warehouse_id, o.total_amount
            FROM orders o
            LEFT JOIN customers c ON c.id=o.customer_id
            ORDER BY o.id
        """)
        for r in cur.fetchall():
            print(r)

        cur.close()

    finally:
        conn.close()

if __name__ == '__main__':
    main()
