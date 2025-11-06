import sqlite3
import os

# Удаляем старую базу, если уже существует
if os.path.exists("cinema.db"):
    os.remove("cinema.db")

# Подключение
conn = sqlite3.connect("cinema.db")
cursor = conn.cursor()

# Создание таблиц
cursor.executescript("""
CREATE TABLE Genres (
    GenreID INTEGER PRIMARY KEY,
    GenreName TEXT
);

CREATE TABLE Movies (
    MovieID INTEGER PRIMARY KEY,
    Title TEXT,
    Year INTEGER,
    GenreID INTEGER,
    FOREIGN KEY (GenreID) REFERENCES Genres(GenreID)
);

CREATE TABLE Halls (
    HallID INTEGER PRIMARY KEY,
    HallName TEXT,
    Capacity INTEGER
);

CREATE TABLE Sessions (
    SessionID INTEGER PRIMARY KEY,
    MovieID INTEGER,
    HallID INTEGER,
    SessionDate TEXT,
    TicketPrice REAL,
    FOREIGN KEY (MovieID) REFERENCES Movies(MovieID),
    FOREIGN KEY (HallID) REFERENCES Halls(HallID)
);

CREATE TABLE Customers (
    CustomerID INTEGER PRIMARY KEY,
    FirstName TEXT,
    LastName TEXT,
    City TEXT
);

CREATE TABLE Tickets (
    TicketID INTEGER PRIMARY KEY,
    SessionID INTEGER,
    CustomerID INTEGER,
    SeatNumber TEXT,
    FOREIGN KEY (SessionID) REFERENCES Sessions(SessionID),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);
""")

# Заполнение таблиц
cursor.executemany("INSERT INTO Genres VALUES (?, ?);", [
    (1, "Боевик"),
    (2, "Комедия"),
    (3, "Фантастика")
])

cursor.executemany("INSERT INTO Movies VALUES (?, ?, ?, ?);", [
    (1, "Мстители", 2019, 3),
    (2, "Джентльмены", 2020, 2),
    (3, "Бэтмен", 2022, 1)
])

cursor.executemany("INSERT INTO Halls VALUES (?, ?, ?);", [
    (1, "Зал 1", 100),
    (2, "Зал 2", 80)
])

cursor.executemany("INSERT INTO Sessions VALUES (?, ?, ?, ?, ?);", [
    (1, 1, 1, "2024-05-01 19:00", 2500),
    (2, 2, 2, "2024-05-02 18:00", 2000),
    (3, 3, 1, "2024-05-03 20:00", 3000),
    (4, 1, 2, "2024-05-05 21:00", 2700)
])

cursor.executemany("INSERT INTO Customers VALUES (?, ?, ?, ?);", [
    (1, "Иван", "Петров", "Алматы"),
    (2, "Мария", "Иванова", "Астана"),
    (3, "Олег", "Сидоров", "Алматы"),
    (4, "Инна", "Ким", "Караганда")
])

cursor.executemany("INSERT INTO Tickets VALUES (?, ?, ?, ?);", [
    (1, 1, 1, "A1"),
    (2, 2, 1, "B2"),
    (3, 1, 2, "A2"),
    (4, 3, 3, "C3"),
    (5, 4, 1, "A3"),  # Иван Петров купил уже 3 билета на разные сеансы
    (6, 3, 2, "B1"),
    (7, 4, 3, "C2")
])

conn.commit()

# Выполняем запрос
print("Результат запроса (клиенты с >=2 билетами на разные сеансы):\n")

cursor.execute("""
SELECT 
    m.Title AS MovieTitle,
    g.GenreName,
    s.SessionDate,
    c.FirstName,
    c.LastName,
    c.City,
    s.TicketPrice
FROM Tickets t
JOIN Sessions s ON t.SessionID = s.SessionID
JOIN Movies m ON s.MovieID = m.MovieID
JOIN Genres g ON m.GenreID = g.GenreID
JOIN Customers c ON t.CustomerID = c.CustomerID
WHERE c.CustomerID IN (
    SELECT CustomerID
    FROM Tickets
    GROUP BY CustomerID
    HAVING COUNT(DISTINCT SessionID) >= 2
)
ORDER BY s.SessionDate;
""")

for row in cursor.fetchall():
    print(row)

conn.close()
print("\nБаза данных сохранена как cinema.db")
