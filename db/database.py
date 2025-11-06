import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

DATABASE_PATH = "vpn.db"

@contextmanager
def get_db_connection():
    """
    Контекстный менеджер для подключения к базе данных
    """
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """
    Инициализирует базу данных и создает таблицы
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Создаем таблицу пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                start_date TEXT,
                end_date TEXT,
                v2ray_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()

def get_user(user_id: int):
    """
    Получает информацию о пользователе по его ID
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        if row:
            return {
                'user_id': row[0],
                'start_date': row[1],
                'end_date': row[2],
                'v2ray_id': row[3],
                'created_at': row[4]
            }
        return None

def create_user(user_id: int, end_date: str):
    """
    Создает нового пользователя
    """
    start_date = datetime.now().isoformat()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO users (user_id, start_date, end_date) VALUES (?, ?, ?)",
            (user_id, start_date, end_date)
        )
        conn.commit()

def update_subscription(user_id: int, new_end_date: str):
    """
    Обновляет дату окончания подписки пользователя
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET end_date = ? WHERE user_id = ?",
            (new_end_date, user_id)
        )
        conn.commit()

def get_active_users():
    """
    Получает список всех активных пользователей
    """
    current_time = datetime.now().isoformat()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE end_date IS NOT NULL AND end_date > ?",
            (current_time,)
        )
        rows = cursor.fetchall()
        
        users = []
        for row in rows:
            users.append({
                'user_id': row[0],
                'start_date': row[1],
                'end_date': row[2],
                'v2ray_id': row[3],
                'created_at': row[4]
            })
        return users

def save_user_v2ray_id(user_id: int, v2ray_id: str):
    """
    Сохраняет v2ray ID пользователя
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET v2ray_id = ? WHERE user_id = ?",
            (v2ray_id, user_id)
        )
        conn.commit()

def get_user_v2ray_id(user_id: int):
    """
    Получает v2ray ID пользователя
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT v2ray_id FROM users WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else None

# Инициализируем базу данных при импорте модуля
init_db()
