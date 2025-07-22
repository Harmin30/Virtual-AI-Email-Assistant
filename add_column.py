import sqlite3

def add_reminder_sent_column(db_path='emails.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if the column already exists
    cursor.execute("PRAGMA table_info(email_status);")
    columns = [info[1] for info in cursor.fetchall()]
    if 'reminder_sent' not in columns:
        print("Adding 'reminder_sent' column...")
        cursor.execute("ALTER TABLE email_status ADD COLUMN reminder_sent BOOLEAN DEFAULT 0;")
        print("'reminder_sent' column added successfully.")
    else:
        print("'reminder_sent' column already exists. No changes made.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_reminder_sent_column()
