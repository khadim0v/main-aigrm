from pymongo import MongoClient

# Подключение к MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Создание базы данных movieDB
db = client["movieDB"]

# Создание коллекции movies
movies = db["movies"]

# Очистим коллекцию, чтобы не дублировать данные
movies.delete_many({})

# Данные о фильмах
movies_data = [
    {
        "title": "Достать ножи",
        "year": 2019,
        "genre": "Детектив",
        "rating": 8.0
    },
    {
        "title": "Главный герой",
        "year": 2021,
        "genre": "Комедия",
        "rating": 7.3
    },
    {
        "title": "Интерстеллар",
        "year": 2014,
        "genre": "Фантастика",
        "rating": 8.6
    }
]

# Добавление фильмов в коллекцию
result = movies.insert_many(movies_data)

print(f"Добавлено {len(result.inserted_ids)} фильма(ов) в коллекцию 'movies'.")
