#!/usr/bin/env python3
"""
social_network_all_in_one.py

Однофайловая демонстрация проектирования и реализации базы данных для упрощённой социальной сети.
Включает:
 - модели SQLAlchemy для пользователей, постов, комментариев, личных и групповых чатов;
 - хеширование паролей (argon2 через passlib, с запасным вариантом PBKDF2 если passlib не установлен);
 - шифрование сообщений (AES-GCM через cryptography) — серверное шифрование;
 - создание БД (SQLite по умолчанию), наполнение тестовыми данными и демонстрация выборок.

Запуск:
 1) Установите зависимости (рекомендуется):
    pip install sqlalchemy passlib cryptography
    # Если хотите argon2 через passlib: pip install "passlib[argon2]"

 2) Запустите:
    python social_network_all_in_one.py

Примечание:
 - Скрипт использует SQLite для простоты. Для продакшна замените DATABASE_URL на PostgreSQL/MySQL.
 - Если некоторые библиотеки не установлены, скрипт всё равно создаст файл БД и выполнит операции
   с безопасными запасными реализациями (PBKDF2 для паролей). Для шифрования сообщений cryptography
   рекомендуется; если она отсутствует, сообщения будут сохранены в поле encrypted_payload в виде
   открытого текста, а encryption_scheme='PLAINTEXT' (но скрипт напомнит, что это небезопасно).
"""

import os
import sys
import binascii
import hmac
from datetime import datetime

# --------- Опциональные зависимости (попытаемся импортировать) ----------
_have_sqlalchemy = True
_have_passlib = True
_have_crypto = True

try:
    from sqlalchemy import (
        create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text, LargeBinary, func
    )
    from sqlalchemy.orm import declarative_base, relationship, sessionmaker
except Exception as e:
    _have_sqlalchemy = False
    sqlalchemy_error = e

try:
    from passlib.hash import argon2
except Exception:
    _have_passlib = False

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except Exception:
    _have_crypto = False

# ------------------ Конфигурация --------------------
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///social_network.db")
DEMO_AES_KEY = None  # будет сгенерирован в рантайме, если cryptography доступен

# ------------------ Хеширование паролей --------------------
if _have_passlib:
    def hash_password(password: str) -> str:
        return argon2.hash(password)

    def verify_password(password: str, hashed: str) -> bool:
        try:
            return argon2.verify(password, hashed)
        except Exception:
            return False
else:
    import hashlib
    import os as _os
    def hash_password(password: str) -> str:
        # PBKDF2-HMAC-SHA256 запасной вариант (не так удобен как argon2, но лучше чем plain)
        salt = _os.urandom(16)
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 200_000)
        return binascii.hexlify(salt).decode() + '$' + binascii.hexlify(dk).decode()

    def verify_password(password: str, hashed: str) -> bool:
        try:
            salt_hex, dk_hex = hashed.split('$')
            salt = binascii.unhexlify(salt_hex)
            expected = binascii.unhexlify(dk_hex)
            dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 200_000)
            return hmac.compare_digest(dk, expected)
        except Exception:
            return False

# ------------------ Шифрование сообщений (серверное AES-GCM) --------------------
if _have_crypto:
    import os as _os
    def generate_aes_key() -> bytes:
        return _os.urandom(32)  # AES-256

    def encrypt_message_aes_gcm(plaintext: str, key: bytes):
        aes = AESGCM(key)
        nonce = _os.urandom(12)
        ct = aes.encrypt(nonce, plaintext.encode('utf-8'), None)
        # AESGCM returns ciphertext||tag; мы храним их вместе
        return ct, nonce

    def decrypt_message_aes_gcm(ct: bytes, nonce: bytes, key: bytes) -> str:
        aes = AESGCM(key)
        pt = aes.decrypt(nonce, ct, None)
        return pt.decode('utf-8')
else:
    def encrypt_message_aes_gcm(plaintext: str, key: bytes):
        # небезопасный fallback: сохраняем в открытом виде, но помечаем как PLAINTEXT
        return plaintext.encode('utf-8'), b''

    def decrypt_message_aes_gcm(ct: bytes, nonce: bytes, key: bytes) -> str:
        return ct.decode('utf-8')

# ------------------ Проверим наличие SQLAlchemy и определим модели --------------------
if not _have_sqlalchemy:
    print("ERROR: SQLAlchemy не установлен в этой среде.")
    print("Установите зависимости и запустите файл локально:")
    print("  pip install sqlalchemy passlib cryptography")
    sys.exit(1)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(String(36), primary_key=True)  # можно использовать UUID строки
    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    password_hash = Column(String(512), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    bio = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    sent_private_messages = relationship("PrivateMessage", back_populates="sender", cascade="all, delete-orphan")
    sent_group_messages = relationship("GroupMessage", back_populates="sender", cascade="all, delete-orphan")

class Post(Base):
    __tablename__ = "posts"
    post_id = Column(String(36), primary_key=True)
    author_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"
    comment_id = Column(String(36), primary_key=True)
    post_id = Column(String(36), ForeignKey("posts.post_id", ondelete="CASCADE"))
    author_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"))
    parent_comment_id = Column(String(36), ForeignKey("comments.comment_id", ondelete="SET NULL"), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)

    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")

class Follow(Base):
    __tablename__ = "follows"
    follower_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    followee_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Личные чаты (гибкая модель: чат с 2+ участниками)
class PrivateChat(Base):
    __tablename__ = "private_chats"
    chat_id = Column(String(36), primary_key=True)
    is_direct = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_archived = Column(Boolean, default=False, nullable=False)

    members = relationship("PrivateChatMember", back_populates="chat", cascade="all, delete-orphan")
    messages = relationship("PrivateMessage", back_populates="chat", cascade="all, delete-orphan")

class PrivateChatMember(Base):
    __tablename__ = "private_chat_members"
    chat_id = Column(String(36), ForeignKey("private_chats.chat_id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    chat = relationship("PrivateChat", back_populates="members")

class PrivateMessage(Base):
    __tablename__ = "private_messages"
    message_id = Column(String(36), primary_key=True)
    chat_id = Column(String(36), ForeignKey("private_chats.chat_id", ondelete="CASCADE"))
    sender_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"))
    encrypted_payload = Column(LargeBinary, nullable=False)
    encryption_scheme = Column(String(64), nullable=False)  # e.g., AES-256-GCM, E2EE-...
    key_id = Column(String(128), nullable=True)  # идентификатор ключа в KMS, если есть
    nonce = Column(LargeBinary, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)

    chat = relationship("PrivateChat", back_populates="messages")
    sender = relationship("User", back_populates="sent_private_messages")

# Групповые чаты
class GroupChat(Base):
    __tablename__ = "group_chats"
    group_id = Column(String(36), primary_key=True)
    name = Column(String(200), nullable=True)
    owner_id = Column(String(36), ForeignKey("users.user_id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_private = Column(Boolean, default=True, nullable=False)

    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    messages = relationship("GroupMessage", back_populates="group", cascade="all, delete-orphan")

class GroupMember(Base):
    __tablename__ = "group_members"
    group_id = Column(String(36), ForeignKey("group_chats.group_id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    role = Column(String(32), default="member", nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    group = relationship("GroupChat", back_populates="members")

class GroupMessage(Base):
    __tablename__ = "group_messages"
    message_id = Column(String(36), primary_key=True)
    group_id = Column(String(36), ForeignKey("group_chats.group_id", ondelete="CASCADE"))
    sender_id = Column(String(36), ForeignKey("users.user_id", ondelete="CASCADE"))
    encrypted_payload = Column(LargeBinary, nullable=False)
    encryption_scheme = Column(String(64), nullable=False)
    key_id = Column(String(128), nullable=True)
    nonce = Column(LargeBinary, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)

    group = relationship("GroupChat", back_populates="messages")
    sender = relationship("User", back_populates="sent_group_messages")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    audit_id = Column(Integer, primary_key=True, autoincrement=True)
    actor_id = Column(String(36), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    action = Column(String(200), nullable=False)
    object_type = Column(String(100), nullable=True)
    object_id = Column(String(36), nullable=True)
    metadata_json = Column(Text, nullable=True)  # renamed from 'metadata' to avoid conflict with Declarative API
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ------------------ Утилиты --------------------
import uuid
from sqlalchemy.exc import IntegrityError

def gen_id() -> str:
    return str(uuid.uuid4())

def get_engine(url=DATABASE_URL):
    return create_engine(url, echo=False, future=True)

SessionLocal = None

def create_db(engine):
    Base.metadata.create_all(bind=engine)
    print("База данных и таблицы созданы или уже существовали.")

# ------------------ CRUD / демонстрация --------------------
def create_user(session, username: str, email: str, password: str):
    u = User(
        user_id=gen_id(),
        username=username,
        email=email,
        password_hash=hash_password(password),
    )
    session.add(u)
    try:
        session.commit()
        session.refresh(u)
        print(f"Пользователь создан: {u.username} ({u.user_id})")
        return u
    except IntegrityError:
        session.rollback()
        print("Ошибка: пользователь с таким именем или email уже существует.")
        return None

def create_post(session, author: User, content: str):
    p = Post(post_id=gen_id(), author_id=author.user_id, content=content)
    session.add(p)
    session.commit()
    session.refresh(p)
    print(f"Пост создан: {p.post_id}")
    return p

def create_comment(session, post: Post, author: User, content: str, parent_comment_id=None):
    c = Comment(comment_id=gen_id(), post_id=post.post_id, author_id=author.user_id, content=content, parent_comment_id=parent_comment_id)
    session.add(c)
    session.commit()
    session.refresh(c)
    print(f"Комментарий создан: {c.comment_id}")
    return c

def create_private_chat(session, member_user_ids):
    chat = PrivateChat(chat_id=gen_id(), is_direct=(len(member_user_ids) == 2))
    session.add(chat)
    for uid in member_user_ids:
        m = PrivateChatMember(chat_id=chat.chat_id, user_id=uid)
        session.add(m)
    session.commit()
    session.refresh(chat)
    print(f"Личный чат создан: {chat.chat_id}")
    return chat

def send_private_message(session, chat: PrivateChat, sender: User, plaintext: str, key: bytes=None, key_id: str=None):
    global DEMO_AES_KEY
    if key is None and _have_crypto:
        key = DEMO_AES_KEY
    if _have_crypto:
        ct, nonce = encrypt_message_aes_gcm(plaintext, key)
        scheme = "AES-256-GCM"
        payload = ct
    else:
        # предупреждение: PLAINTEXT сохраняется небезопасно
        payload, nonce = encrypt_message_aes_gcm(plaintext, key)
        scheme = "PLAINTEXT"
    msg = PrivateMessage(
        message_id=gen_id(),
        chat_id=chat.chat_id,
        sender_id=sender.user_id,
        encrypted_payload=payload,
        encryption_scheme=scheme,
        key_id=key_id,
        nonce=nonce
    )
    session.add(msg)
    session.commit()
    session.refresh(msg)
    print(f"Отправлено сообщение {msg.message_id} в чат {chat.chat_id} (scheme={scheme})")
    return msg

def read_and_decrypt_private_messages(session, chat: PrivateChat, key: bytes=None):
    global DEMO_AES_KEY
    if key is None and _have_crypto:
        key = DEMO_AES_KEY
    msgs = session.query(PrivateMessage).filter(PrivateMessage.chat_id == chat.chat_id).order_by(PrivateMessage.created_at).all()
    result = []
    for m in msgs:
        try:
            if m.encryption_scheme == "AES-256-GCM" and _have_crypto:
                pt = decrypt_message_aes_gcm(m.encrypted_payload, m.nonce, key)
            elif m.encryption_scheme == "PLAINTEXT":
                pt = m.encrypted_payload.decode('utf-8')
            else:
                pt = "<неизвестная схема>"
        except Exception as e:
            pt = f"<ошибка расшифровки: {e}>"
        result.append((m.message_id, m.sender_id, pt, m.encryption_scheme, m.created_at))
    return result

# ------------------ Заполнение тестовыми данными и демонстрация --------------------
def seed_and_demo(engine):
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = Session()
    # Проверка, есть ли пользователи
    if session.query(User).first() is not None:
        print("Данные уже присутствуют — seed пропущен.")
        session.close()
        return

    # создаём ключ для демонстрации, если возможно
    global DEMO_AES_KEY
    if _have_crypto:
        DEMO_AES_KEY = generate_aes_key()
        print("DEMO AES key generated for encryption demo.")
    else:
        print("cryptography не обнаружен — сообщения будут сохранены в открытом виде (PLAINTEXT).")

    # создаём пользователей
    u1 = create_user(session, "ivan", "ivan@example.com", "password123")
    u2 = create_user(session, "maria", "maria@example.com", "securepass")
    if not u1 or not u2:
        session.close()
        return

    # пост и комментарий
    p1 = create_post(session, u1, "Привет! Это мой первый пост.")
    c1 = create_comment(session, p1, u2, "Отличный пост!")

    # личный чат и сообщения
    chat = create_private_chat(session, [u1.user_id, u2.user_id])
    send_private_message(session, chat, u1, "Привет, Мария! Это приватное сообщение.")
    send_private_message(session, chat, u2, "Привет, Иван! Получил твоё сообщение.")

    # прочитаем и декодируем
    msgs = read_and_decrypt_private_messages(session, chat)
    print("\nПрочитанные сообщения в чате:")
    for m in msgs:
        print(f"  id={m[0]} sender={m[1]} scheme={m[3]} text={m[2]}")

    session.close()

# ------------------ Основная точка входа --------------------
def main():
    print("Запуск demo social_network_all_in_one.py")
    print(f"SQLAlchemy available: {_have_sqlalchemy}")
    print(f"passlib available: {_have_passlib} (если False — используется PBKDF2 запасной вариант)")
    print(f"cryptography available: {_have_crypto} (если False — сообщения будут PLAINTEXT)")

    engine = get_engine()
    create_db(engine)
    seed_and_demo(engine)
    print("\nГотово. Файл БД:", os.path.abspath(os.path.join(".", "social_network.db")))

if __name__ == "__main__":
    main()
