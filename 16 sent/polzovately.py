import sqlite3
import os

# Удаляем старую базу, если есть
if os.path.exists("social_likes.db"):
    os.remove("social_likes.db")

# Подключаемся
conn = sqlite3.connect("social_likes.db")
cursor = conn.cursor()

# Создаем таблицы
cursor.executescript("""
CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY,
    username TEXT
);

CREATE TABLE Posts (
    post_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    post_content TEXT,
    likes_count INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
""")

# Добавляем пользователей
cursor.executemany("INSERT INTO Users VALUES (?, ?);", [
    (1, "ivan"),
    (2, "maria"),
    (3, "alex"),
    (4, "olga")
])

# Добавляем посты
cursor.executemany("INSERT INTO Posts VALUES (?, ?, ?, ?);", [
    (1, 1, "Первый пост Ивана", 10),
    (2, 1, "Второй пост Ивана", 5),
    (3, 2, "Пост Марии", 8),
    (4, 3, "Пост Алекса", 0)
])

conn.commit()

# SQL-запрос: пользователи + сумма лайков
print("Пользователи и общее количество лайков:\n")
cursor.execute("""
SELECT 
    u.username,
    COALESCE(SUM(p.likes_count), 0) AS total_likes
FROM Users u
LEFT JOIN Posts p ON u.user_id = p.user_id
GROUP BY u.user_id, u.username;
""")

for row in cursor.fetchall():
    print(row)

conn.close()
print("\nБаза данных сохранена как social_likes.db")
