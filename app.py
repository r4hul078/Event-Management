from flask import Flask, request, jsonify, redirect, url_for, render_template, session
import sqlite3

import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure key


UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Database
def init_db():
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                profile_picture TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except sqlite3.Error as error:
        print('Database Error:', error)

init_db()

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Login route with session handling
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    data = request.json
    email = data.get('email')
    password = data.get('password')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email FROM users WHERE email = ? AND password = ?', (email, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['user_id'] = user[0]
        session['name'] = user[1]
        session['email'] = user[2]
        return jsonify({'redirect': url_for('dashboard')})
    else:
        return jsonify({'error': 'Invalid email or password'})


# Dashboard route (Protected)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    context  = {
        'name' : session['name'],
        'email': session['email'],
        'page': 'dashboard'    
    }
    return render_template('dashboard.html', **context)

# Register Route

@app.route('/register-user')
def registerUser():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    if 'profile_picture' not in request.files:
        return jsonify({'error': 'Profile picture is required'}), 400

    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    profile_picture = request.files['profile_picture']

    if not name or not email or not password or not confirm_password:
        return jsonify({'error': 'All fields are required'}), 400

    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400

    filename = secure_filename(profile_picture.filename)
    profile_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    profile_picture.save(profile_path)

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()

    if user:
        conn.close()
        return jsonify({'error': 'Email already registered'}), 400

    cursor.execute('INSERT INTO users (name, email, password, profile_picture) VALUES (?, ?, ?, ?)', 
                   (name, email, password, filename))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    # Store user session
    session['user_id'] = user_id
    session['name'] = name
    session['email'] = email
    session['profile_picture'] = filename

    return jsonify({'success': True, 'redirect': url_for('dashboard')})


@app.route('/user-detail')
def userDetail():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Fetch only the logged-in user's details
    cursor.execute('SELECT id, name ,email, profile_picture FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    
    conn.close()
    context = {
        'user': user,
        'page': 'user-detail' 
    }
    return render_template('user-detail.html', **context)


@app.route('/update-user', methods=['POST'])
def update_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return jsonify({'error': 'Both fields are required'}), 400

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Update user in the database
    cursor.execute('UPDATE users SET name = ?, email = ? WHERE id = ?', (name, email, session['user_id']))
    conn.commit()
    conn.close()

    # Update session data
    session['name'] = name
    session['email'] = email

    return jsonify({'success': True})


# Logout route
@app.route('/logout')
def logout():
    session.clear()  # Clears all session data
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
