from database import get_db_connection

try:
    conn = get_db_connection()
    print("MySQL connection successful!")
    conn.close()
except Exception as e:
    print("MySQL connection failed:")
    print(e)
