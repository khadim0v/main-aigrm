from pymongo import MongoClient
from datetime import datetime, timedelta
from prettytable import PrettyTable  # pip install prettytable

# Подключение к MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["userDB"]
users = db["users"]

# Очистим коллекцию и добавим тестовые данные
users.delete_many({})
users.insert_many([
    {
        "name": "Антон",
        "loginHistory": [
            {"date": datetime(2025, 10, 1), "action": "login"},
            {"date": datetime(2025, 10, 10), "action": "logout"}
        ]
    },
    {
        "name": "Мария",
        "loginHistory": [
            {"date": datetime(2025, 10, 28), "action": "login"}
        ]
    }
])

# 1. Найти пользователей, которые не входили последние 7 дней
cutoff_date = datetime.utcnow() - timedelta(days=7)
inactive_users = users.find({
    "loginHistory": {
        "$not": {
            "$elemMatch": {
                "action": "login",
                "date": {"$gte": cutoff_date}
            }
        }
    }
})

print("1. Пользователи, не входившие в систему последние 7 дней:")
inactive_table = PrettyTable(["Имя пользователя", "Последний вход"])
for u in inactive_users:
    # Найдём последнюю дату входа
    logins = [entry["date"] for entry in u["loginHistory"] if entry["action"] == "login"]
    last_login = max(logins) if logins else "Нет входов"
    inactive_table.add_row([u["name"], last_login.strftime("%Y-%m-%d %H:%M:%S") if isinstance(last_login, datetime) else last_login])
print(inactive_table)
print()

# 2. Добавить новую запись о входе с текущей датой
now = datetime.utcnow()
users.update_many({}, {"$push": {"loginHistory": {"date": now, "action": "login"}}})
print("2. Добавлена запись о входе с текущей датой всем пользователям.\n")

# 3. Удалить все записи logout старше месяца
month_ago = datetime.utcnow() - timedelta(days=30)
users.update_many(
    {},
    {"$pull": {"loginHistory": {"action": "logout", "date": {"$lt": month_ago}}}}
)
print("3. Удалены все записи logout старше месяца.\n")

# 4. Красивый вывод текущего состояния коллекции
print("Текущее состояние пользователей:\n")
table = PrettyTable(["Имя", "Последний вход", "Количество логов"])
for doc in users.find({}, {"_id": 0}):
    logins = [entry["date"] for entry in doc["loginHistory"] if entry["action"] == "login"]
    last_login = max(logins) if logins else None
    table.add_row([
        doc["name"],
        last_login.strftime("%Y-%m-%d %H:%M:%S") if last_login else "—",
        len(doc["loginHistory"])
    ])
print(table)
