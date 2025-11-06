from pymongo import MongoClient
from datetime import datetime

# Подключение к локальной базе MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["warehouse"]           # база данных
inventory = db["inventory"]        # коллекция

# 1. Найти все товары, у которых количество меньше 10
low_stock = inventory.find({"quantity": {"$lt": 10}})
print("Товары, у которых количество меньше 10:")
for item in low_stock:
    print(item)

# 2. Вывести среднюю цену по каждой категории
avg_prices = inventory.aggregate([
    {
        "$group": {
            "_id": "$category",
            "avgPrice": {"$avg": "$price"}
        }
    }
])
print("\nСредняя цена по категориям:")
for cat in avg_prices:
    print(f"{cat['_id']}: {cat['avgPrice']:.2f}")

# 3. Увеличить цену всех товаров из категории 'Электроника' на 10%
inventory.update_many(
    {"category": "Электроника"},
    [{"$set": {"price": {"$multiply": ["$price", 1.1]}}}]
)
print("\nЦены в категории 'Электроника' увеличены на 10%.")

# 4. Удалить товары, которых нет в наличии (quantity = 0)
delete_result = inventory.delete_many({"quantity": 0})
print(f"\nУдалено товаров без наличия: {delete_result.deleted_count}")
