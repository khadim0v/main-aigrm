# online_library.py
from datetime import datetime
import hashlib
from typing import Optional, List

from sqlalchemy import (
    create_engine, Column, Integer, String, Date, Text, ForeignKey, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Файл БД: online_library.db (SQLite)
DATABASE_URL = "sqlite:///online_library.db"

Base = declarative_base()


def hash_password(plain: str) -> str:
    """Простейшее хеширование пароля (для демонстрации)."""
    return hashlib.sha256(plain.encode("utf-8")).hexdigest()


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)  # хранится хэш
    registration_date = Column(Date, default=datetime.utcnow)

    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")


class Author(Base):
    __tablename__ = "authors"

    author_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(150), nullable=False)
    birth_year = Column(Integer, nullable=True)

    books = relationship("Book", back_populates="author", cascade="all, delete-orphan")


class Genre(Base):
    __tablename__ = "genres"

    genre_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)

    books = relationship("Book", back_populates="genre", cascade="all, delete-orphan")


class Book(Base):
    __tablename__ = "books"

    book_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    publish_year = Column(Integer, nullable=True)

    author_id = Column(Integer, ForeignKey("authors.author_id", onupdate="CASCADE", ondelete="SET NULL"))
    genre_id = Column(Integer, ForeignKey("genres.genre_id", onupdate="CASCADE", ondelete="SET NULL"))

    author = relationship("Author", back_populates="books")
    genre = relationship("Genre", back_populates="books")
    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="rating_range_check"),
    )

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.book_id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    review_date = Column(Date, default=datetime.utcnow)

    user = relationship("User", back_populates="reviews")
    book = relationship("Book", back_populates="reviews")


# Создание движка и сессии
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def create_db():
    """Создаёт таблицы в базе (если ещё не созданы)."""
    Base.metadata.create_all(bind=engine)
    print("База и таблицы созданы (если ещё не существовали).")


# CRUD-утилиты
def add_user(session, name: str, email: str, password_plain: str) -> User:
    user = User(name=name, email=email, password=hash_password(password_plain), registration_date=datetime.utcnow())
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def add_author(session, full_name: str, birth_year: Optional[int] = None) -> Author:
    author = Author(full_name=full_name, birth_year=birth_year)
    session.add(author)
    session.commit()
    session.refresh(author)
    return author


def add_genre(session, name: str) -> Genre:
    genre = Genre(name=name)
    session.add(genre)
    session.commit()
    session.refresh(genre)
    return genre


def add_book(session, title: str, publish_year: Optional[int], author: Author, genre: Genre) -> Book:
    book = Book(title=title, publish_year=publish_year, author=author, genre=genre)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


def add_review(session, user: User, book: Book, rating: int, comment: Optional[str] = None) -> Review:
    if rating < 1 or rating > 5:
        raise ValueError("rating must be between 1 and 5")
    review = Review(user=user, book=book, rating=rating, comment=comment, review_date=datetime.utcnow())
    session.add(review)
    session.commit()
    session.refresh(review)
    return review


def get_book_reviews(session, book_id: int) -> List[Review]:
    return session.query(Review).filter(Review.book_id == book_id).order_by(Review.review_date.desc()).all()


def get_user_reviews(session, user_id: int) -> List[Review]:
    return session.query(Review).filter(Review.user_id == user_id).order_by(Review.review_date.desc()).all()


def get_average_rating(session, book_id: int) -> Optional[float]:
    from sqlalchemy import func
    avg = session.query(func.avg(Review.rating)).filter(Review.book_id == book_id).scalar()
    return float(avg) if avg is not None else None


def seed_example_data():
    """Добавляет пару записей для примера работы."""
    with SessionLocal() as session:
        # Проверка — если уже есть данные, не будем дублировать
        exists = session.query(User).first()
        if exists:
            print("Данные уже присутствуют — seed пропущен.")
            return

        u1 = add_user(session, "Иван Иванов", "ivan@example.com", "password123")
        u2 = add_user(session, "Мария Петрова", "maria@example.com", "securepass")

        a1 = add_author(session, "Фёдор Достоевский", 1821)
        a2 = add_author(session, "Лев Толстой", 1828)

        g1 = add_genre(session, "Роман")
        g2 = add_genre(session, "Классика")

        b1 = add_book(session, "Преступление и наказание", 1866, a1, g2)
        b2 = add_book(session, "Война и мир", 1869, a2, g1)

        add_review(session, u1, b1, 5, "Глубокое произведение, рекомендую.")
        add_review(session, u2, b1, 4, "Сильные персонажи, тяжеловато читать.")
        add_review(session, u1, b2, 5, "Эпическая картина эпохи.")

        print("Примеры данных добавлены.")


def demo_queries():
    with SessionLocal() as session:
        # Список книг и их среднего рейтинга
        books = session.query(Book).all()
        print("\nКниги и средний рейтинг:")
        for b in books:
            avg = get_average_rating(session, b.book_id)
            print(f"  [{b.book_id}] {b.title} ({b.publish_year}) — автор: {b.author.full_name if b.author else '—'} — жанр: {b.genre.name if b.genre else '—'} — средний рейтинг: {avg or 'нет отзывов'}")

        # Отзывы для конкретной книги (например, первая)
        if books:
            book = books[0]
            print(f"\nОтзывы для книги: {book.title}")
            reviews = get_book_reviews(session, book.book_id)
            for r in reviews:
                print(f"  {r.review_date} — {r.user.name} — рейтинг: {r.rating} — {r.comment}")


if __name__ == "__main__":
    create_db()
    seed_example_data()
    demo_queries()
