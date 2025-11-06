from pymongo import MongoClient
from datetime import datetime

# Подключаемся к MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Создаём базу данных eduPlatform
db = client["eduPlatform"]

# Создаём коллекцию courses
courses = db["courses"]

# Очищаем коллекцию (чтобы не дублировалось при повторных запусках)
courses.delete_many({})

# Добавляем два курса
courses_data = [
    {
        "title": "Python с нуля",
        "description": "Основы программирования на Python для начинающих.",
        "category": "Программирование",
        "price": 4990,
        "published": True,
        "created_at": datetime(2023, 6, 10, 10, 0, 0),
        "teacher": {
            "name": "Иван Петров",
            "email": "ivan.petrov@example.com",
            "experience_years": 5
        },
        "lessons": [
            {"title": "Введение", "duration_min": 15, "video_url": "https://video.example.com/intro"},
            {"title": "Основы", "duration_min": 25, "video_url": "https://video.example.com/basics"}
        ],
        "students": [
            {"name": "Алексей Попов", "email": "alex@example.com", "progress": 60},
            {"name": "Мария Козлова", "email": "maria@example.com", "progress": 100}
        ]
    },
    {
        "title": "Веб-разработка на JavaScript",
        "description": "Изучение основ веб-программирования и фреймворков.",
        "category": "Программирование",
        "price": 4500,
        "published": True,
        "created_at": datetime(2023, 8, 15, 10, 0, 0),
        "teacher": {
            "name": "Елена Смирнова",
            "email": "elena.smirnova@example.com",
            "experience_years": 7
        },
        "lessons": [
            {"title": "HTML и CSS", "duration_min": 20, "video_url": "https://video.example.com/html"},
            {"title": "JavaScript основы", "duration_min": 30, "video_url": "https://video.example.com/js"}
        ],
        "students": [
            {"name": "Дмитрий Орлов", "email": "dmitry@example.com", "progress": 40},
            {"name": "Светлана Иванова", "email": "svetlana@example.com", "progress": 90}
        ]
    }
]

# Вставляем документы
courses.insert_many(courses_data)

# 1. Найти все опубликованные курсы
print("1. Опубликованные курсы:")
for course in courses.find({"published": True}):
    print("-", course["title"])

# 2. Найти курсы категории «Программирование» с ценой < 5000
print("\n2. Курсы категории 'Программирование' с ценой < 5000:")
for course in courses.find({"category": "Программирование", "price": {"$lt": 5000}}):
    print("-", course["title"])

# 3. Найти курсы, где есть студент с прогрессом < 50%
print("\n3. Курсы, где есть студент с прогрессом < 50%:")
for course in courses.find({"students.progress": {"$lt": 50}}):
    print("-", course["title"])

# 4. Получить имена преподавателей всех курсов
print("\n4. Преподаватели всех курсов:")
teachers = courses.distinct("teacher.name")
for name in teachers:
    print("-", name)
