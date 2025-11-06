from pymongo import MongoClient

# Подключение к MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["peopleDB"]
users = db["users"]

# Очистим коллекцию
users.delete_many({})

# Добавим примеры данных
users.insert_many([
    {"name": "Анна", "age": 22, "contacts": {"email": "anna@mail.ru", "phone": "12345"}},
    {"name": "Иван", "age": 30, "contacts": {"email": "ivan@mail.ru", "phone": "77777"}},
    {"name": "Мария", "age": 19, "contacts": {"email": "maria@mail.ru", "phone": "88888"}},
    {"name": "Олег", "age": 40, "contacts": {"email": "ivan@mail.ru", "phone": "99999"}},  # дубликат email
])

# 1. Изменить номер телефона на "555-555" у Анны
users.update_one({"name": "Анна"}, {"$set": {"contacts.phone": "555-555"}})
print("1. Телефон Анны изменён на 555-555\n")

# 2. Найти документы, где поле "contacts.email" существует и является строкой
print("2. Документы с существующим email строкового типа:")
query = {
    "contacts.email": {"$exists": True, "$type": "string"}
}
for doc in users.find(query, {"_id": 0, "name": 1, "contacts.email": 1}):
    print(doc)

# 3. Подсчитать, сколько пользователей младше 25 лет
count_young = users.count_documents({"age": {"$lt": 25}})
print(f"\n3. Количество пользователей младше 25 лет: {count_young}")

# 4. Удалить документы, у которых одинаковое значение поля "contacts.email"
print("\n4. Удаляем пользователей с дублирующими email...")

# Соберем все email и посчитаем количество повторений
from collections import Counter

emails = [u["contacts"]["email"] for u in users.find({"contacts.email": {"$exists": True}})]
duplicates = [email for email, count in Counter(emails).items() if count > 1]

# Удаляем все документы с дублирующими email
if duplicates:
    users.delete_many({"contacts.email": {"$in": duplicates}})

# Проверим оставшиеся документы
print("Оставшиеся пользователи:")
for doc in users.find({}, {"_id": 0, "name": 1, "contacts.email": 1}):
    print(doc)
