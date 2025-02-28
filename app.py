from flask import Flask, request, jsonify, redirect, render_template, session, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "mysecretkey"

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def setup_database():
    if not os.path.exists("users.db"):
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                address TEXT UNIQUE NOT NULL,
                phone INTEGER,
                password TEXT NOT NULL,
                profile_picture TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                event_name TEXT,
                event_date TEXT,
                venue TEXT,
                description TEXT,
                address TEXT,
                phone_number TEXT,
                paid INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()
        conn.close()
        print("Database and tables created.")
    else:
        print("Database already exists, skipping setup.")

setup_database()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    try:
        email = request.json["email"]
        password = request.json["password"]
        print("Trying to log in with email:", email, "and password:", password)
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session["user_id"] = user[0]
            print("Login successful, user_id:", user[0])
            return jsonify({"redirect": "/dashboard"})
        else:
            print("Login failed: No matching user")
            return jsonify({"error": "Wrong email or password"})
    except Exception as e:
        print("Login error:", str(e))
        return jsonify({"error": "Something went wrong"})


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        print("No user session, redirecting to login")
        return redirect("/login")
    return render_template("dashboard.html")


@app.route("/events", methods=["GET"])
def get_events():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"})
    user_id = session["user_id"]
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, event_name, event_date, venue, description, address, phone_number, paid FROM events WHERE user_id = ?", (user_id,))
    events = cursor.fetchall()
    conn.close()
    event_list = []
    for event in events:
        event_list.append({
            "id": event[0],
            "name": event[1],
            "date": event[2],
            "venue": event[3],
            "description": event[4],
            "address": event[5],
            "phone_number": event[6],
            "paid": event[7]
        })
    print("Sending events:", event_list)
    return jsonify({"events": event_list})


@app.route("/events", methods=["POST"])
def add_event():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"})
    data = request.json
    user_id = session["user_id"]
    event_name = data["event_name"]
    event_date = data["event_date"]
    venue = data["venue"]
    description = data["description"]
    address = data["address"]
    phone_number = data["phone_number"]
    if not event_name or not event_date or not venue or not description or not address or not phone_number:
        return jsonify({"error": "Please fill all fields!"})
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO events (user_id, event_name, event_date, venue, description, address, phone_number) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (user_id, event_name, event_date, venue, description, address, phone_number))
    conn.commit()
    conn.close()
    return jsonify({"success": True})



# DEL event
@app.route("/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    user_id = session["user_id"]
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE id = ? AND user_id = ?", (event_id, user_id))
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"error": "Event not found or not authorized"}), 404
    conn.commit()
    conn.close()
    return jsonify({"success": True})



@app.route('/user-detail')
def userDetail():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, profile_picture, address, phone FROM users WHERE id = ?', (session['user_id'],))
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
    cursor.execute('UPDATE users SET name = ?, email = ? WHERE id = ?', (name, email, session['user_id']))
    conn.commit()
    conn.close()
    session['name'] = name
    session['email'] = email
    return jsonify({'success': True})



@app.route('/register', methods=['GET'])
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
    address = request.form.get('address')
    phone = request.form.get('phone')
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
    cursor.execute('INSERT INTO users (name, email, password, profile_picture, address, phone) VALUES (?, ?, ?, ?, ?, ?)', 
                   (name, email, password, filename, address, phone))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    session['user_id'] = user_id
    session['name'] = name
    session['email'] = email
    session['profile_picture'] = filename
    return jsonify({'success': True, 'redirect': url_for('dashboard')})



@app.route("/pay/<int:event_id>", methods=["POST"])
def pay_event(event_id):
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"})
    user_id = session["user_id"]
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE events SET paid = 1 WHERE id = ? AND user_id = ?", (event_id, user_id))
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"error": "Event not found"})
    conn.commit()
    conn.close()
    return jsonify({"success": True})




@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("user_id", None)
    if request.method == "POST":
        return jsonify({"success": True, "redirect": "/login"})
    return redirect("/login")




if __name__ == "__main__":
    app.run(debug=True)