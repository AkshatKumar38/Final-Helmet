import sqlite3

conn = sqlite3.connect("data/employee_data.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM employees")
users = cursor.fetchall()

print("Current Users in Database:")
for user in users:
    print(user)

conn.close()
