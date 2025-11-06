import sqlite3

# Создаём и подключаем базу данных
conn = sqlite3.connect("campaigns.db")
cursor = conn.cursor()

# Удаляем таблицу, если существует
cursor.execute("DROP TABLE IF EXISTS CampaignResults")

# Создаём таблицу
cursor.execute("""
CREATE TABLE CampaignResults (
    campaign_id INTEGER PRIMARY KEY,
    clicks INTEGER,
    conversions REAL,
    budget REAL
)
""")

# Добавляем тестовые данные
data = [
    (1, 5000, 7000, 5000),   # ROI = 140 → Успех
    (2, 3000, 4000, 4000),   # ROI = 100 → Средне
    (3, 2000, 1000, 2000),   # ROI = 50 → Провал
    (4, 10000, 12000, 8000), # ROI = 150 → Успех
    (5, 4000, 3500, 5000)    # ROI = 70 → Провал
]
cursor.executemany("INSERT INTO CampaignResults VALUES (?, ?, ?, ?)", data)

# SQL-запрос с IIF для оценки успеха
cursor.execute("""
SELECT 
    campaign_id,
    ROUND((conversions * 100.0) / budget, 2) AS ROI,
    IIF((conversions * 100.0) / budget > 120, 'Успех',
        IIF((conversions * 100.0) / budget >= 80, 'Средне', 'Провал')
    ) AS success_level
FROM CampaignResults
""")

# Вывод результатов
print("Результаты кампаний:")
for campaign_id, roi, level in cursor.fetchall():
    print(f"Кампания {campaign_id}: ROI = {roi}%, Оценка — {level}")

# Сохраняем и закрываем
conn.commit()
conn.close()

print("\nБаза данных сохранена в campaigns.db")
