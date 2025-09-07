# import sqlite3
# from datetime import datetime

# DB_NAME = "emails.db"

# # ------------------------
# # Database Initialization
# # ------------------------
# def init_db():
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()

#     # Create the emails table if it doesn't exist
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS emails (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             sender TEXT,
#             subject TEXT,
#             classification TEXT,
#             summary TEXT,
#             timestamp TEXT,
#             read INTEGER DEFAULT 0
#         )
#     ''')

#     conn.commit()
#     conn.close()


# # ------------------------
# # Core Email Operations
# # ------------------------
# def add_email(sender, subject, classification, summary, timestamp):
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     cursor.execute('''
#         INSERT INTO emails (sender, subject, classification, summary, timestamp)
#         VALUES (?, ?, ?, ?, ?)
#     ''', (sender, subject, classification, summary, timestamp))
#     conn.commit()
#     conn.close()


# def get_emails(unread_only=False, query=""):
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     base_query = "SELECT * FROM emails"
#     filters = []
#     args = []

#     if unread_only:
#         filters.append("read = 0")
#     if query:
#         filters.append("(" +
#             "sender LIKE ? OR subject LIKE ? OR classification LIKE ? OR summary LIKE ?" +
#         ")")
#         args += [f"%{query}%"] * 4

#     if filters:
#         base_query += " WHERE " + " AND ".join(filters)

#     base_query += " ORDER BY timestamp DESC"
#     cursor.execute(base_query, args)
#     emails = cursor.fetchall()
#     conn.close()
#     return emails


# def mark_as_read(email_id):
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     cursor.execute("UPDATE emails SET read = 1 WHERE id = ?", (email_id,))
#     conn.commit()
#     conn.close()

import sqlite3
from datetime import datetime

DB_NAME = "emails.db"

# ------------------------
# Database Initialization
# ------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create emails table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            subject TEXT,
            classification TEXT,
            summary TEXT,
            timestamp TEXT,
            read INTEGER DEFAULT 0
        )
    ''')

    # Create users table with is_admin column (if it doesn't exist yet)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            is_admin INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()


# ------------------------
# Migration: add is_admin column if missing
# ------------------------
def migrate_add_is_admin():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if "is_admin" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        print("Added is_admin column to users table.")
    else:
        print("is_admin column already exists.")
    conn.commit()
    conn.close()


# ------------------------
# Email Operations
# ------------------------
def add_email(sender, subject, classification, summary, timestamp):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO emails (sender, subject, classification, summary, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (sender, subject, classification, summary, timestamp))
    conn.commit()
    conn.close()


def get_emails(unread_only=False, query=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    base_query = "SELECT * FROM emails"
    filters = []
    args = []

    if unread_only:
        filters.append("read = 0")
    if query:
        filters.append("(" +
            "sender LIKE ? OR subject LIKE ? OR classification LIKE ? OR summary LIKE ?" +
        ")")
        args += [f"%{query}%"] * 4

    if filters:
        base_query += " WHERE " + " AND ".join(filters)

    base_query += " ORDER BY timestamp DESC"
    cursor.execute(base_query, args)
    emails = cursor.fetchall()
    conn.close()
    return emails


def mark_as_read(email_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE emails SET read = 1 WHERE id = ?", (email_id,))
    conn.commit()
    conn.close()


# ------------------------
# User Operations
# ------------------------
def add_user(email, password, role="user", is_admin=0):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (email, password, role, is_admin) VALUES (?, ?, ?, ?)",
        (email, password, role, is_admin)
    )
    conn.commit()
    conn.close()


def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, role, is_admin FROM users")
    users = cursor.fetchall()
    conn.close()
    return users


def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


def get_user_by_email(email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

