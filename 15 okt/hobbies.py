from pymongo import MongoClient

# Подключаемся к MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["peopleDB"]
users = db["users"]

# Очищаем коллекцию для чистоты эксперимента
users.delete_many({})

# Добавляем тестовые данные
users.insert_many([
    {"name": "Петр", "hobbies": ["футбол", "шахматы", "чтение"]},
    {"name": "Анна", "hobbies": ["танцы", "чтение"]},
    {"name": "Иван", "hobbies": ["футбол", "программирование"]}
])

# 1. Найти всех пользователей, у которых есть хобби "футбол"
print("Пользователи, у которых есть хобби 'футбол':")
for user in users.find({"hobbies": "футбол"}, {"_id": 0, "name": 1, "hobbies": 1}):
    print(user)

# 2. Добавить новое хобби "программирование" всем пользователям (если его ещё нет)
users.update_many(
    {"hobbies": {"$ne": "программирование"}},
    {"$push": {"hobbies": "программирование"}}
)

# 3. Удалить хобби "чтение" у всех пользователей
users.update_many(
    {},
    {"$pull": {"hobbies": "чтение"}}
)

# Проверим итог
print("\nКоллекция после изменений:")
for user in users.find({}, {"_id": 0, "name": 1, "hobbies": 1}):
    print(user)
