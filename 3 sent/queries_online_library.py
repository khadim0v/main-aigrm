# queries_online_library.py
# Создаёт БД (SQLite), наполняет примерными данными и выполняет 3 запроса,
# затем выводит результаты в терминал.

import sqlite3

DB = "online_library_sqlite.db"

schema_sql = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    registration_date DATE DEFAULT (DATE('now'))
);

CREATE TABLE IF NOT EXISTS Authors (
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    birth_year INTEGER
);

CREATE TABLE IF NOT EXISTS Genres (
    genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    publish_year INTEGER,
    author_id INTEGER REFERENCES Authors(author_id) ON DELETE SET NULL ON UPDATE CASCADE,
    genre_id INTEGER REFERENCES Genres(genre_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    book_id INTEGER NOT NULL REFERENCES Books(book_id) ON DELETE CASCADE ON UPDATE CASCADE,
    rating INTEGER NOT NULL,
    comment TEXT,
    review_date DATE DEFAULT (DATE('now')),
    CHECK (rating BETWEEN 1 AND 5)
);
"""

seed_sql = """
INSERT OR IGNORE INTO Authors(author_id, full_name, birth_year) VALUES (1, 'Фёдор Достоевский', 1821);
INSERT OR IGNORE INTO Authors(author_id, full_name, birth_year) VALUES (2, 'Лев Толстой', 1828);

INSERT OR IGNORE INTO Genres(genre_id, name) VALUES (1, 'Классика');
INSERT OR IGNORE INTO Genres(genre_id, name) VALUES (2, 'Роман');

INSERT OR IGNORE INTO Books(book_id, title, publish_year, author_id, genre_id) VALUES (1, 'Преступление и наказание', 1866, 1, 1);
INSERT OR IGNORE INTO Books(book_id, title, publish_year, author_id, genre_id) VALUES (2, 'Война и мир', 1869, 2, 2);

INSERT OR IGNORE INTO Users(user_id, name, email, password, registration_date) VALUES (1, 'Иван Иванов', 'ivan@example.com', 'hash1', DATE('2025-01-01'));
INSERT OR IGNORE INTO Users(user_id, name, email, password, registration_date) VALUES (2, 'Мария Петрова', 'maria@example.com', 'hash2', DATE('2025-02-02'));

INSERT OR IGNORE INTO Reviews(review_id, user_id, book_id, rating, comment, review_date) VALUES (1, 1, 1, 5, 'Глубокое произведение, рекомендую.', DATE('2025-03-01'));
INSERT OR IGNORE INTO Reviews(review_id, user_id, book_id, rating, comment, review_date) VALUES (2, 2, 1, 4, 'Сильные персонажи, тяжеловато читать.', DATE('2025-03-05'));
INSERT OR IGNORE INTO Reviews(review_id, user_id, book_id, rating, comment, review_date) VALUES (3, 1, 2, 5, 'Эпическая картина эпохи.', DATE('2025-03-10'));
"""

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.executescript(schema_sql)
    cur.executescript(seed_sql)
    conn.commit()

    print("База и примерные данные готовы.\n")

    # 1) Все отзывы для одной книги (book_id = 1)
    book_id = 1
    cur.execute("""
    SELECT r.review_id, u.name, r.rating, r.comment, r.review_date
    FROM Reviews r
    JOIN Users u ON r.user_id = u.user_id
    WHERE r.book_id = ?
    ORDER BY r.review_date DESC;
    """, (book_id,))
    reviews = cur.fetchall()

    print(f"1) Все отзывы для книги с id={book_id}:\n")
    if not reviews:
        print("  Отзывов нет.\n")
    else:
        for rev in reviews:
            print(f"  review_id={rev[0]} | user={rev[1]} | rating={rev[2]} | date={rev[4]}")
            print(f"    comment: {rev[3]}")
        print("")

    # 2) Книги со средним рейтингом >= threshold (в нашей схеме шкала 1-5)
    threshold = 4.0
    cur.execute("""
    SELECT b.book_id, b.title, ROUND(AVG(r.rating), 2) as avg_rating, COUNT(r.review_id) as reviews_count
    FROM Books b
    JOIN Reviews r ON b.book_id = r.book_id
    GROUP BY b.book_id
    HAVING avg_rating >= ?
    ORDER BY avg_rating DESC;
    """, (threshold,))
    books_above = cur.fetchall()

    print(f"2) Книги с средним рейтингом >= {threshold}:\n")
    if not books_above:
        print("  Нет книг, соответствующих условию.\n")
    else:
        for bk in books_above:
            print(f"  book_id={bk[0]} | title={bk[1]} | avg_rating={bk[2]} | reviews={bk[3]}")
        print("")

    # 3) Список книг жанра 'Классика'
    genre_name = "Классика"
    cur.execute("""
    SELECT b.book_id, b.title, b.publish_year, a.full_name
    FROM Books b
    LEFT JOIN Authors a ON b.author_id = a.author_id
    LEFT JOIN Genres g ON b.genre_id = g.genre_id
    WHERE g.name = ?
    ORDER BY b.title;
    """, (genre_name,))
    books_genre = cur.fetchall()

    print(f"3) Список книг жанра '{genre_name}':\n")
    if not books_genre:
        print("  Нет книг в этом жанре.\n")
    else:
        for bk in books_genre:
            print(f"  book_id={bk[0]} | title={bk[1]} | year={bk[2]} | author={bk[3]}")
        print("")

    conn.close()

if __name__ == "__main__":
    main()
