from flask import Flask, request, jsonify, redirect, url_for, render_template
import sqlite3

app = Flask(__name__)

#Database
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


init_db()


#starting route
@app.route('/')
def index():
    return render_template('index.html')

#Login page ko lagi
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    data = request.json
    email = data.get('email')
    password = data.get('password')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({'redirect': url_for('dashboard')})
    else:
        return jsonify({'error': 'Invalid email or password'})

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'})

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()

    
    if user: #Yesle chai aba fetch gareko user database ma xaki nai vanera check garxa
        conn.close()
        return jsonify({'error': 'Email already registered'}), 400

    cursor.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'redirect': '/login'})

if __name__ == '__main__':
    app.run(debug=True)