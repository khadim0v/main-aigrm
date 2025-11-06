from pymongo import MongoClient
from bson.son import SON

# Подключение к MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["companyDB"]
employees = db["employees"]
departments = db["departments"]

# Очистим коллекции, чтобы не было дубликатов
employees.delete_many({})
departments.delete_many({})

# Добавим тестовые данные
departments.insert_many([
    {"_id": 10, "name": "Маркетинг"},
    {"_id": 20, "name": "Разработка"},
    {"_id": 30, "name": "Продажи"}
])

employees.insert_many([
    {"_id": 1, "name": "Олег", "department_id": 10, "salary": 95000},
    {"_id": 2, "name": "Анна", "department_id": 20, "salary": 120000},
    {"_id": 3, "name": "Игорь", "department_id": 20, "salary": 110000},
    {"_id": 4, "name": "Мария", "department_id": 30, "salary": 80000}
])

# 1. Объединение коллекций (join) — имя сотрудника и его отдел
print("1. Сотрудники и их отделы:")
pipeline = [
    {
        "$lookup": {
            "from": "departments",
            "localField": "department_id",
            "foreignField": "_id",
            "as": "department"
        }
    },
    {"$unwind": "$department"},
    {"$project": {"_id": 0, "name": 1, "department": "$department.name"}}
]
for doc in employees.aggregate(pipeline):
    print(doc)

# 2. Средняя зарплата по каждому отделу
print("\n2. Средняя зарплата по отделам:")
pipeline = [
    {"$group": {"_id": "$department_id", "avg_salary": {"$avg": "$salary"}}},
    {
        "$lookup": {
            "from": "departments",
            "localField": "_id",
            "foreignField": "_id",
            "as": "department"
        }
    },
    {"$unwind": "$department"},
    {"$project": {"_id": 0, "department": "$department.name", "avg_salary": 1}}
]
for doc in employees.aggregate(pipeline):
    print(doc)

# 3. Добавить новый отдел и перенести туда одного сотрудника
print("\n3. Добавляем новый отдел и переносим туда сотрудника:")
departments.insert_one({"_id": 40, "name": "HR"})
employees.update_one({"name": "Олег"}, {"$set": {"department_id": 40}})
for doc in employees.find({}, {"_id": 0, "name": 1, "department_id": 1}):
    print(doc)

# 4. Удалить отдел, в котором нет сотрудников
print("\n4. Удаляем отделы без сотрудников:")
# Получаем ID всех отделов, у которых нет сотрудников
used_departments = employees.distinct("department_id")
departments.delete_many({"_id": {"$nin": used_departments}})
for doc in departments.find({}, {"_id": 1, "name": 1}):
    print(doc)

# 5. Найти всех сотрудников с зарплатой выше средней по их отделу
print("\n5. Сотрудники с зарплатой выше средней по их отделу:")
# Сначала найдём среднюю по каждому отделу
avg_salaries = {
    d["_id"]: d["avg_salary"]
    for d in employees.aggregate([
        {"$group": {"_id": "$department_id", "avg_salary": {"$avg": "$salary"}}}
    ])
}

# Теперь фильтруем сотрудников по этому критерию
for emp in employees.find():
    dep_avg = avg_salaries.get(emp["department_id"])
    if dep_avg and emp["salary"] > dep_avg:
        print({"name": emp["name"], "salary": emp["salary"], "department_id": emp["department_id"]})
