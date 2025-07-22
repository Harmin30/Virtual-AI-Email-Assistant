import sqlite3
from datetime import datetime

DB_NAME = "emails.db"

# ------------------------
# Database Initialization
# ------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create the emails table if it doesn't exist
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

    conn.commit()
    conn.close()


# ------------------------
# Core Email Operations
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
