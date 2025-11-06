from pymongo import MongoClient
from datetime import datetime, timedelta
import random
import string

# Подключение к MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["testdb"]        # Название базы данных
users_collection = db["users"]  # Коллекция users

# Очистим коллекцию перед вставкой (по желанию)
users_collection.delete_many({})

# Функция генерации случайного имени
def random_name():
    return ''.join(random.choices(string.ascii_letters, k=7)).capitalize()

# Функция генерации случайного email
def random_email(name):
    domains = ["gmail.com", "mail.ru", "yahoo.com", "outlook.com"]
    return f"{name.lower()}@{random.choice(domains)}"

# Генерация 100 случайных пользователей
users = []
for _ in range(100):
    name = random_name()
    age = random.randint(18, 65)
    email = random_email(name)
    # Случайная дата регистрации за последние 365 дней
    registered_at = datetime.now() - timedelta(days=random.randint(0, 365))
    
    user = {
        "name": name,
        "age": age,
        "email": email,
        "registered_at": registered_at
    }
    users.append(user)

# Вставка всех пользователей в MongoDB
result = users_collection.insert_many(users)
print(f"Добавлено {len(result.inserted_ids)} пользователей в коллекцию 'users'.")
