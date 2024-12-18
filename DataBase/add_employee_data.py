import sqlite3

DB_PATH = "data/employee_data.db"  # Path to your database file

# Connect to the database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Function to insert new employee data
def add_employee(username, password):
    try:
        cursor.execute("INSERT INTO employees (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        print(f"User '{username}' added successfully!")
    except sqlite3.IntegrityError:
        print(f"Error: User '{username}' already exists!")

# Add new employees
add_employee("new_user", "password123")
add_employee("employee1", "securepass")
add_employee("employee2", "mypassword")

# Close the connection
conn.close()
print("Data insertion completed.")
