import sqlite3

DB_PATH = "data/employee_data.db"  # Path to your database file

# Connect to SQLite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create table for employee credentials
cursor.execute('''
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# Insert sample data (for testing purposes)
cursor.execute("INSERT OR IGNORE INTO employees (username, password) VALUES ('admin', 'admin123')")
cursor.execute("INSERT OR IGNORE INTO employees (username, password) VALUES ('user', 'password123')")

# Commit and close
conn.commit()
conn.close()

print("Database created and sample data added!")
