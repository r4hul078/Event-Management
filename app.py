from flask import Flask, request, jsonify, redirect, render_template, session
import sqlite3

app = Flask(__name__)
app.secret_key = "mysecretkey"

# This function sets up the database without test data
def setup_database():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT, password TEXT)")
    cursor.execute("DROP TABLE IF EXISTS events")  # Start fresh
    cursor.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, user_id INTEGER, event_name TEXT, event_date TEXT, venue TEXT, description TEXT, address TEXT, phone_number TEXT, paid INTEGER DEFAULT 0)")
    conn.commit()
    # No test user or event inserted
    print("Database is ready with empty tables!")
    conn.close()

setup_database()

# Home page
@app.route("/")
def home():
    return render_template("index.html")

# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    try:
        email = request.json["email"]
        password = request.json["password"]
        print("Trying to log in with email:", email, "and password:", password)  # Debug
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session["user_id"] = user[0]  # Remember the user
            print("Login successful, user_id:", user[0])  # Debug
            return jsonify({"redirect": "/dashboard"})
        else:
            print("Login failed: No matching user")  # Debug
            return jsonify({"error": "Wrong email or password"})
    except Exception as e:
        print("Login error:", str(e))  # Debug
        return jsonify({"error": "Something went wrong"})

# Dashboard page
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        print("No user session, redirecting to login")  # Debug
        return redirect("/login")
    return render_template("dashboard.html")

# Get events from the database
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
    print("Sending events:", event_list)  # Debug
    return jsonify({"events": event_list})

# Add a new event to the database
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

# Get user details
@app.route("/user-details", methods=["GET"])
def get_user_details():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"})
    user_id = session["user_id"]
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    print("Sending user email:", user[0])  # Debug
    return jsonify({"email": user[0]})

# Register a new user
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    data = request.json
    email = data["email"]
    password = data["password"]
    if not email or not password:
        return jsonify({"error": "Need email and password!"})
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Email already used"})
    cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "redirect": "/login"})

# Mark an event as paid
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

# Log the user out
@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"success": True, "redirect": "/login"})

if __name__ == "__main__":
    app.run(debug=True)