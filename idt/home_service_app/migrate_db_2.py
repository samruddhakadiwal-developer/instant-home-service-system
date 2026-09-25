import sqlite3

def run_migration():
    conn = sqlite3.connect("home_service_email.db")
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE service_requests ADD COLUMN car_size VARCHAR")
        cursor.execute("ALTER TABLE service_requests ADD COLUMN carpentry_size VARCHAR")
        cursor.execute("ALTER TABLE service_requests ADD COLUMN photo_data VARCHAR")
        print("Added columns to service_requests table")
    except Exception as e:
        print(f"Error (maybe already exist?): {e}")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    run_migration()
