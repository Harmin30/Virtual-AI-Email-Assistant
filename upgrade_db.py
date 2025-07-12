import sqlite3

DB_PATH = 'emails.db'  # Replace with your actual DB file if different

def add_column_if_not_exists():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if the column already exists
    cursor.execute("PRAGMA table_info(email_status)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'smart_reply' not in columns:
        print("⏳ Adding 'smart_reply' column...")
        cursor.execute("ALTER TABLE email_status ADD COLUMN smart_reply TEXT")
        print("✅ 'smart_reply' column added successfully.")
    else:
        print("ℹ️ 'smart_reply' column already exists — no action taken.")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    add_column_if_not_exists()
