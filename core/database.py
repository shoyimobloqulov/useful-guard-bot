import sqlite3
from datetime import datetime

DB_NAME = 'members.db'

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE, 
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            joined_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def is_user_exists(user_id):
    """Foydalanuvchi bazada borligini tekshirish"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM group_members WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def add_member(user_id, first_name, last_name, username):
    """Foydalanuvchini bazaga qo'shish (faqat yangilar uchun)"""
    conn = get_connection()
    cursor = conn.cursor()
    joined_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO group_members (user_id, first_name, last_name, username, joined_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, first_name, last_name, username, joined_at))
        conn.commit()
    finally:
        conn.close()