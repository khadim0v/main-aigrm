from pymongo import MongoClient
from pprint import pprint

# Подключение к MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["weatherDB"]
weather = db["weather"]

# Очищаем коллекцию
weather.delete_many({})

# Добавляем данные
weather.insert_many([
    {"city": "Алматы", "month": "Январь", "temperature": -5},
    {"city": "Алматы", "month": "Февраль", "temperature": -2},
    {"city": "Алматы", "month": "Март", "temperature": 5},
    {"city": "Нур-Султан", "month": "Январь", "temperature": -15},
    {"city": "Нур-Султан", "month": "Февраль", "temperature": -10},
    {"city": "Нур-Султан", "month": "Март", "temperature": -2},
])

# 1. Средняя температура по каждому городу
avg_temp = weather.aggregate([
    {"$group": {"_id": "$city", "avg_temperature": {"$avg": "$temperature"}}}
])
print("Средняя температура по городам:")
for doc in avg_temp:
    pprint(doc)

# 2. Месяц с самой высокой температурой
highest_temp = weather.find_one(sort=[("temperature", -1)])
print("\nМесяц с самой высокой температурой:")
pprint(highest_temp)

# 3. Добавить поле season по месяцу
seasons_map = {
    "Декабрь": "Зима", "Январь": "Зима", "Февраль": "Зима",
    "Март": "Весна", "Апрель": "Весна", "Май": "Весна",
    "Июнь": "Лето", "Июль": "Лето", "Август": "Лето",
    "Сентябрь": "Осень", "Октябрь": "Осень", "Ноябрь": "Осень"
}

for doc in weather.find():
    season = seasons_map.get(doc["month"], "Неизвестно")
    weather.update_one({"_id": doc["_id"]}, {"$set": {"season": season}})

print("\nКоллекция после добавления поля 'season':")
for doc in weather.find():
    pprint(doc)
