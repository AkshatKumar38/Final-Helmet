from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
import sqlite3
import matplotlib.pyplot as plt
from io import BytesIO
import pandas as pd
import subprocess
import base64
import time,os,sys
import signal
from flask_cors import CORS
from threading import Lock
from flask import g
db_lock = Lock()

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Paths to data files
EXCEL_FILE_PATH = "data/helmet_data.xlsx"
DB_PATH = "data/helmet_data.db"
DB_PATH_E = "data/employee_data.db"
DB_PATH_H = "data/helmets.db"
# Utility function for the first database connection
def connect_db_main():
    return sqlite3.connect(DB_PATH)

# Utility function for the second database connection
def connect_db_secondary():
    return sqlite3.connect(DB_PATH_E)
import sqlite3

# Utility function for the helmet database connection
def connect_db():
    # Path to your database file
    return sqlite3.connect('data/helmet.db')


# Function to initialize or access the existing helmets database
def init_db():
    db_path = 'data/helmets.db'
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS helmets (helmet_id INTEGER PRIMARY KEY,status TEXT CHECK(status IN ('active', 'offline')))''')
    conn.commit()
    conn.close()
    


@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = connect_db_secondary()  # Connect to your employee database
        cursor = conn.cursor()

        # Query to check if user exists in the database
        cursor.execute("SELECT username FROM employee_data WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        conn.close()

        if user:  # If user is found
            session['username'] = user[0]  # Store username in session
            return redirect(url_for('dashboard'))
        else:
            return "Invalid Credentials!", 401

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        # Connect to the employee_data database
        conn = connect_db_secondary()
        cursor = conn.cursor()

        try:
            # Insert new user into employee_data table
            cursor.execute("INSERT INTO employee_data (username, password, email) VALUES (?, ?, ?)", 
                           (username, password, email))
            conn.commit()  # Save changes
            conn.close()   # Close connection
            return redirect(url_for('login'))  # Redirect to login page
        except sqlite3.IntegrityError:
            # Handle duplicate username error
            conn.close()
            return "Username already exists. Please choose a different one.", 400

    # Render the registration form
    return render_template('register.html')


@app.route('/index')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    db_path = 'data/helmets.db'  # Ensure this is the correct path

    # Connect to the database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # Execute a query to get the helmets data
    c.execute("SELECT helmet_id, status FROM helmets")  # Ensure table and column names are correct
    helmets = c.fetchall()
    
    conn.close()

    # Check if helmets data is returned and pass it to the template
    if helmets:
        helmet_data = [{"helmet_id": helmet[0], "status": helmet[1]} for helmet in helmets]
    else:
        helmet_data = []

    return render_template('index.html', helmets=helmet_data, username=session['username'])    

# Start the helmet monitoring script as a subprocess
subprocess.Popen(["python", "helmet_status_monitor.py"])  # Adjust the path as needed
# subprocess.Popen(["python", "generated_data.py"])  # Adjust the path as needed

# Home route (Dashboard)
@app.route('/')
def index():
    conn = connect_db_main()
    cursor = conn.cursor()

    # Fetch the latest 10 helmets (based on timestamp or rowid)
    cursor.execute("SELECT DISTINCT rowid, co_level, timestamp FROM sensor_data ORDER BY timestamp DESC LIMIT 10")
    helmets = cursor.fetchall()

    conn.close()

    # Generate a dummy list of helmets (1 to 10 for example purposes)
    helmets = [(i,) for i in range(1, 11)]
    active_helmet = helmets[0]  # Set the first helmet as active

    # Render the dashboard template with helmet data and the logged-in username
    return render_template('index.html', helmets=helmets, active_helmet=active_helmet, username=session['username'])

# Helmet detail page
@app.route('/helmet/<int:helmet_id>')
def helmet_detail(helmet_id):
    conn = connect_db_main()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sensor_data WHERE rowid = ? ORDER BY timestamp DESC", (helmet_id,))
    rows = cursor.fetchall()

    cursor.execute("SELECT timestamp, co_level FROM sensor_data WHERE rowid = ?", (helmet_id,))
    data = cursor.fetchall()
    conn.close()

    timestamps, co_levels = zip(*data) if data else ([], [])

    # Plot the data
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, co_levels, marker='o')
    plt.title(f"CO Levels for Helmet {helmet_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("CO Level")
    plt.xticks(rotation=45)
    plt.tight_layout()

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('helmet_detail.html', helmet_id=helmet_id, data=rows, plot_url=plot_url)

# Fetch recent helmet data
@app.route('/get_helmet_data', methods=['GET'])
def get_helmet_data():
    try:
        data = pd.read_excel(EXCEL_FILE_PATH).dropna().tail(5)
        response = {
            'labels': data['timestamps'].astype(str).tolist(),
            'values': data['co_levels'].tolist(),
        }
    except Exception as e:
        response = {'error': str(e)}

    return jsonify(response)

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

@app.route('/user_management')
def user_management():
    # Get the database connection
    conn = get_db()
    c = conn.cursor()

    # Query the total helmets
    c.execute("SELECT COUNT(*) FROM helmets")
    total_helmets = c.fetchone()[0]

    # Query the active helmets
    c.execute("SELECT COUNT(*) FROM helmets WHERE status = 'online'")
    active_helmets = c.fetchone()[0]

    # Query the offline helmets
    c.execute("SELECT COUNT(*) FROM helmets WHERE status = 'offline'")
    offline_helmets = c.fetchone()[0]

    # Render the user management page and pass the data to the template
    return render_template('user_management.html', total_helmets=total_helmets,active_helmets=active_helmets, offline_helmets=offline_helmets,username=session.get('username'))


init_db()

@app.route('/add_helmet', methods=['POST'])
def add_helmet():
    helmet_id = request.form['helmet_id']
    status = request.form['status']  # Get the status from the form (either 'offline' or 'active')
    
    with db_lock:  # Prevent multiple threads from writing simultaneously
        try:
            conn = get_db()
            c = conn.cursor()
            
            # Insert the helmet with the selected status into the database.
            c.execute("INSERT INTO helmets (helmet_id, status) VALUES (?, ?)", (helmet_id, status))
            conn.commit()
            
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")
            conn.rollback()
            return "Error: Database is locked.", 500
        
    return redirect(url_for('user_management'))  # Redirect to the user management page

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('data/helmets.db', timeout=30, check_same_thread=False)
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/update_helmet_status', methods=['POST'])
def update_helmet_status():
    helmet_id = request.form['helmet_id']
    status = request.form['status']
    
    db_path = 'data/helmets.db'  # Ensure this is the correct path

    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Update the helmet's status in the database
        c.execute("UPDATE helmets SET status = ? WHERE helmet_id = ?", (status, helmet_id))
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        # Redirect back to the user management page
        return redirect(url_for('user_management'))
    except sqlite3.Error as e:
        conn.close()
        return f"An error occurred: {e}", 500
    
@app.route('/delete_helmet', methods=['POST'])
def delete_helmet():
    helmet_id = request.form['helmet_id']  # Get the helmet_id from the form

    with db_lock:  # Ensure safe database access
        try:
            conn = get_db()  # Get the database connection
            c = conn.cursor()

            # Check if the helmet exists
            c.execute("SELECT * FROM helmets WHERE helmet_id = ?", (helmet_id,))
            helmet = c.fetchone()
            if helmet is None:
                return f"Error: Helmet with ID {helmet_id} not found.", 404

            # Delete the helmet from the database
            c.execute("DELETE FROM helmets WHERE helmet_id = ?", (helmet_id,))
            conn.commit()
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")
            conn.rollback()
            return "Error: Could not delete helmet. Database is locked.", 500

    return redirect(url_for('user_management'))  # Redirect to the user management page

@app.route('/offline_helmets')
def offline_helmets():
    # Logic to retrieve and display offline helmets
    return render_template('offline_helmets.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove user session
    return redirect(url_for('login'))



@app.route('/')
def home():
    return "Server is running."

def graceful_exit(signal, frame):
    print("Shutting down server gracefully...")
    sys.exit(0)
# Attach signal handlers
signal.signal(signal.SIGINT, graceful_exit)  # Handle Ctrl+C
signal.signal(signal.SIGTERM, graceful_exit) # Handle termination signals

if __name__ == '__main__':
    
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Exiting...")
        sys.exit(0)