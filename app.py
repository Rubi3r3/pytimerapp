from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime, date

app = Flask(__name__)

# Create SQLite database and table
conn = sqlite3.connect('timer_app.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        user_pin INTEGER,
        password TEXT NOT NULL,
        first_name TEXT,
        last_name TEXT,
        morning_login DATETIME,
        lunch_logout DATETIME,
        lunch_login DATETIME,
        evening_logout DATETIME
    )
''')
conn.commit()
conn.close()


def get_current_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Routes
@app.route('/')
def welcome():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check authentication from the database
        conn = sqlite3.connect('timer_app.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            return redirect(url_for('dashboard', username=username))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html', error=None)

@app.route('/dashboard/<username>', methods=['GET', 'POST'])
def dashboard(username):
    conn = sqlite3.connect('timer_app.db')
    cursor = conn.cursor()

    message = None  # Initialize message variable

    if request.method == 'POST':
        action = request.form['action']
        timestamp = get_current_timestamp()

        cursor.execute('SELECT {} FROM users WHERE username=?'.format(action), (username,))
        existing_timestamp = cursor.fetchone()

        if existing_timestamp:
            # Check if the existing timestamp is from the current day
            existing_datetime = datetime.strptime(existing_timestamp[0], '%Y-%m-%d %H:%M:%S')
            current_datetime = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

            if existing_datetime.date() == current_datetime.date():
                message = f"You have already logged {action.replace('_', ' ')} today at {existing_timestamp[0]}."
            else:
                # Insert a new row for the new day
                cursor.execute('INSERT INTO users (username, {}) VALUES (?, ?)'.format(action), (username, timestamp))
                conn.commit()
                message = f"Successfully logged {action.replace('_', ' ')} today at {timestamp}."
        else:
            # Insert a new row for the new day
            cursor.execute('INSERT INTO users (username, {}) VALUES (?, ?)'.format(action), (username, timestamp))
            conn.commit()
            message = f"Successfully logged {action.replace('_', ' ')} today at {timestamp}."


    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    user_data = cursor.fetchone()
    conn.close()

    return render_template('dashboard.html', username=username, user_data=user_data, message=message)

if __name__ == '__main__':
    app.run(debug=True, port = 5151)
