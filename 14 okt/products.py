from pymongo import MongoClient

# Подключение к MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["shopDB"]  # создаём/открываем базу данных
products = db["products"]  # создаём/открываем коллекцию

# Очищаем коллекцию, чтобы не было дубликатов
products.delete_many({})

# Добавляем товары
products.insert_many([
    {"name": "Laptop", "category": "Electronics", "price": 450000},
    {"name": "Mouse", "category": "Electronics", "price": 8000},
    {"name": "Desk", "category": "Furniture", "price": 120000},
    {"name": "Chair", "category": "Furniture", "price": 70000}
])

# Запрос: найти все товары категории "Electronics" с ценой выше 10000
# Отсортировать по цене (по возрастанию)
# Показать только имя и цену
print("Товары категории 'Electronics' с ценой > 10000:")
cursor = products.find(
    {"category": "Electronics", "price": {"$gt": 10000}},
    {"_id": 0, "name": 1, "price": 1}
).sort("price", 1)

for item in cursor:
    print(item)
