#!/usr/bin/env python3
"""
shop_game_platform.py

Создаёт SQLite БД для игровой платформы, заполняет таблицы минимальными данными
(5 игроков, 3 игры, 9 матчей + PlayerScores) и выполняет запрошенные аналитические запросы.

Запуск:
    python shop_game_platform.py
"""
import sqlite3
from pathlib import Path

DB = "game_platform.db"

INIT_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Players (
    player_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT,
    registration_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS Games (
    game_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    genre TEXT
);

CREATE TABLE IF NOT EXISTS Matches (
    match_id INTEGER PRIMARY KEY,
    game_id INTEGER NOT NULL REFERENCES Games(game_id) ON DELETE CASCADE,
    match_date DATE NOT NULL
);

-- связывающая таблица: результат игрока в матче
CREATE TABLE IF NOT EXISTS PlayerScores (
    score_id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL REFERENCES Matches(match_id) ON DELETE CASCADE,
    player_id INTEGER NOT NULL REFERENCES Players(player_id) ON DELETE CASCADE,
    score INTEGER NOT NULL,
    kills INTEGER NOT NULL,
    deaths INTEGER NOT NULL,
    is_winner INTEGER NOT NULL DEFAULT 0  -- 1 если победил в матче
);
"""

SEED_SQL = """
-- Players (5)
INSERT OR IGNORE INTO Players(player_id, username, email, registration_date) VALUES
 (1, 'Alice', 'alice@example.com', '2024-02-10'),
 (2, 'Bob',   'bob@example.com',   '2023-11-05'),
 (3, 'Carol', 'carol@example.com', '2024-06-15'),
 (4, 'Dave',  'dave@example.com',  '2022-08-20'),
 (5, 'Eve',   'eve@example.com',   '2024-01-01');

-- Games (3)
INSERT OR IGNORE INTO Games(game_id, title, genre) VALUES
 (1, 'Cyber Arena', 'FPS'),
 (2, 'Space Quest', 'Action'),
 (3, 'Battle Royale','Survival');

-- Matches (9)
INSERT OR IGNORE INTO Matches(match_id, game_id, match_date) VALUES
 (1, 1, '2024-03-01'),
 (2, 2, '2024-02-20'),
 (3, 1, '2024-05-10'),
 (4, 3, '2023-12-01'),
 (5, 1, '2024-07-07'),
 (6, 2, '2024-01-15'),
 (7, 3, '2024-03-22'),
 (8, 1, '2024-09-09'),
 (9, 2, '2024-11-11');

-- PlayerScores (participants & results)
-- Match 1 (Cyber Arena): players 1,2,3 -> winner 1
INSERT OR IGNORE INTO PlayerScores(match_id, player_id, score, kills, deaths, is_winner) VALUES
 (1,1,1500,15,3,1),
 (1,2,1200,10,7,0),
 (1,3,900,5,10,0);

-- Match 2 (Space Quest): players 2,4,5 -> winner 4
INSERT OR IGNORE INTO PlayerScores(match_id, player_id, score, kills, deaths, is_winner) VALUES
 (2,2,800,6,8,0),
 (2,4,1100,12,2,1),
 (2,5,700,4,9,0);

-- Match 3 (Cyber Arena): players 1,2 -> winner 2
INSERT OR IGNORE INTO PlayerScores(match_id, player_id, score, kills, deaths, is_winner) VALUES
 (3,1,1300,12,6,0),
 (3,2,1400,14,4,1);

-- Match 4 (Battle Royale): players 3,4,5 -> winner 5
INSERT OR IGNORE INTO PlayerScores(match_id, player_id, score, kills, deaths, is_winner) VALUES
 (4,3,600,3,7,0),
 (4,4,900,8,6,0),
 (4,5,1600,18,1,1);

-- Match 5 (Cyber Arena): players 2,3,5 -> winner 3
INSERT OR IGNORE INTO PlayerScores(match_id, player_id, score, kills, deaths, is_winner) VALUES
 (5,2,1100,11,5,0),
 (5,3,1700,20,2,1),
 (5,5,300,1,12,0);

-- Match 6 (Space Quest): players 1,5 -> winner 1
INSERT OR IGNORE INTO PlayerScores(match_id, player_id, score, kills, deaths, is_winner) VALUES
 (6,1,1250,13,3,1),
 (6,5,800,7,8,0);

-- Match 7 (Battle Royale): players 2,3,4 -> winner 4
INSERT OR IGNORE INTO PlayerScores(match_id, player_id, score, kills, deaths, is_winner) VALUES
 (7,2,950,9,6,0),
 (7,3,1100,10,5,0),
 (7,4,1450,16,2,1);

-- Match 8 (Cyber Arena): players 4,1 -> winner 1
INSERT OR IGNORE INTO PlayerScores(match_id, player_id, score, kills, deaths, is_winner) VALUES
 (8,4,700,5,9,0),
 (8,1,1800,22,1,1);

-- Match 9 (Space Quest): players 3,5 -> winner 5
INSERT OR IGNORE INTO PlayerScores(match_id, player_id, score, kills, deaths, is_winner) VALUES
 (9,3,1000,8,7,0),
 (9,5,1700,19,0,1); -- note: deaths=0 to test K/D handling
"""

QUERIES = [
    {
        "title": "1) Игроки, зарегистрировавшиеся в 2024 году",
        "sql": """
            SELECT player_id, username, registration_date
            FROM Players
            WHERE registration_date BETWEEN '2024-01-01' AND '2024-12-31'
            ORDER BY player_id;
        """
    },
    {
        "title": "2) Средний балл (score) для игрока с player_id = 1",
        "sql": """
            SELECT p.player_id, p.username,
                   ROUND(AVG(ps.score),2) AS avg_score,
                   COUNT(ps.match_id) AS matches_played
            FROM Players p
            LEFT JOIN PlayerScores ps ON p.player_id = ps.player_id
            WHERE p.player_id = 1
            GROUP BY p.player_id, p.username;
        """
    },
    {
        "title": "3) Топ-5 самых популярных игр по количеству сыгранных матчей (Title, matches_count)",
        "sql": """
            SELECT g.title, COUNT(m.match_id) AS matches_count
            FROM Games g
            LEFT JOIN Matches m ON g.game_id = m.game_id
            GROUP BY g.game_id, g.title
            ORDER BY matches_count DESC, g.title
            LIMIT 5;
        """
    },
    {
        "title": "4) Игрок с самым высоким средним K/D (Kills/Deaths) по всем матчам",
        "sql": """
            SELECT p.player_id, p.username,
                   SUM(ps.kills) AS total_kills,
                   SUM(ps.deaths) AS total_deaths,
                   -- Обработка деления на ноль: если всего смертей = 0, используем очень большое значение
                   CASE WHEN SUM(ps.deaths) = 0 THEN CAST(SUM(ps.kills) AS FLOAT)
                        ELSE ROUND(CAST(SUM(ps.kills) AS FLOAT) / SUM(ps.deaths), 4)
                   END AS kd_ratio
            FROM Players p
            JOIN PlayerScores ps ON p.player_id = ps.player_id
            GROUP BY p.player_id, p.username
            ORDER BY kd_ratio DESC
            LIMIT 1;
        """
    },
    {
        "title": "5) Игроки, которые участвовали в матчах игры 'Cyber Arena' но ни разу не победили в этой игре",
        "sql": """
            SELECT DISTINCT p.player_id, p.username
            FROM Players p
            JOIN PlayerScores ps ON p.player_id = ps.player_id
            JOIN Matches m ON ps.match_id = m.match_id
            JOIN Games g ON m.game_id = g.game_id
            WHERE g.title = 'Cyber Arena'
            GROUP BY p.player_id, p.username
            HAVING SUM(ps.is_winner) = 0
            ORDER BY p.player_id;
        """
    },
    {
        "title": "6) Полная статистика матча с match_id = 2",
        "sql": """
            SELECT m.match_id, m.match_date, g.title AS game_title,
                   p.player_id, p.username, ps.score, ps.kills, ps.deaths, ps.is_winner,
                   CASE WHEN ps.deaths = 0 THEN CAST(ps.kills AS FLOAT)
                        ELSE ROUND(CAST(ps.kills AS FLOAT) / ps.deaths, 4)
                   END AS kd
            FROM Matches m
            JOIN Games g ON m.game_id = g.game_id
            JOIN PlayerScores ps ON m.match_id = ps.match_id
            JOIN Players p ON ps.player_id = p.player_id
            WHERE m.match_id = 2
            ORDER BY ps.is_winner DESC, ps.score DESC;
        """
    },
]

def run_script(conn, script):
    cur = conn.cursor()
    cur.executescript(script)
    conn.commit()

def print_query(conn, title, sql):
    print("\n" + title)
    print("-" * len(title))
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    if not rows:
        print(" (нет результатов)")
        return
    # print header
    cols = [desc[0] for desc in cur.description]
    print(" | ".join(cols))
    print("-" * 60)
    for r in rows:
        print(" | ".join(str(x) if x is not None else "NULL" for x in r))

def main():
    first_time = not Path(DB).exists()
    conn = sqlite3.connect(DB)
    if first_time:
        run_script(conn, INIT_SQL)
        run_script(conn, SEED_SQL)
    else:
        # ensure seed idempotent
        run_script(conn, SEED_SQL)

    for q in QUERIES:
        print_query(conn, q["title"], q["sql"])

    conn.close()

if __name__ == "__main__":
    main()
