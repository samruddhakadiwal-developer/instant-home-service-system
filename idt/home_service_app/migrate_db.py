import sqlite3

def run_migration():
    conn = sqlite3.connect("home_service_email.db")
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN average_rating FLOAT DEFAULT 0.0")
        cursor.execute("ALTER TABLE users ADD COLUMN total_reviews INTEGER DEFAULT 0")
        print("Added columns to users table")
    except Exception as e:
        print(f"User columns error (maybe already exist?): {e}")

    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            rating INTEGER DEFAULT 5,
            comment VARCHAR,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        ''')
        print("Created app_reviews table")
    except Exception as e:
        print(f"App reviews table error: {e}")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    run_migration()
