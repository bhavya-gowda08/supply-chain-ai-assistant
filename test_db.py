from database import get_connection, get_inventory

try:
    connection = get_connection()
    print("MySQL connected successfully!")
    connection.close()

    data = get_inventory()
    print(data)

except Exception as e:
    print("Database connection failed:", e)