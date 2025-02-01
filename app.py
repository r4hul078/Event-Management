from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

# SQLite database file
DATABASE = 'users.db'

# Function to initialize the database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

# Function to check if a user exists
def user_exists(email):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        return cursor.fetchone() is not None

# Function to create a new user
def create_user(username, email, password):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
        ''', (username, email, password))
        conn.commit()

# Route to serve the login page
@app.route('/')
def login_page():
    return render_template('login.html')

# Route to verify or create a user
@app.route('/verify_or_create_user', methods=['POST'])
def verify_or_create_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required"}), 400

    if user_exists(email):
        return jsonify({"message": "User already exists"}), 200
    else:
        create_user(username, email, password)
        return jsonify({"message": "User created successfully"}), 201

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)  # Run the Flask app