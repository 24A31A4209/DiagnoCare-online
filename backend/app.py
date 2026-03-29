import os
import sqlite3
from google import genai
from flask import Flask, render_template, jsonify, request, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from functools import wraps

from flask import send_from_directory


# ===================== CONFIG =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
app.secret_key = "diagnocare_secret_key"  # change in production

#================ GenAi Client ====================

client = genai.Client(api_key="AIzaSyAyQBZP3P3Qa4Vgq3s9_wBhuuXf8ox4gQI")

@app.route("/api/gemini-chat", methods=["POST"])
def gemini_chat():
    user_message = request.json.get("message", "")

    # Call Gemini
    response = client.models.generate_content(
        model="chat-bison-001",  # valid chat model
        prompt=f"You are a helpful healthcare assistant. Reply to the user politely.\nUser: {user_message}\nAssistant:"
    )

    # response.text contains the reply
    return jsonify({"reply": response.text})


@app.route("/chat")
def chat_page():
    return render_template("chat.html")



# ===================== DB CONNECTION =====================
def get_db_connection():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "database.db")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# ===================== AUTH DECORATORS =====================
def login_required_page(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper

def login_required_api(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Login required"}), 401
        return f(*args, **kwargs)
    return wrapper


# ===================== HOME =====================
@app.route("/")
def home():
    user = None
    if "user_id" in session:
        conn = get_db_connection()
        user = conn.execute("""
            SELECT id, name, email, phone, address, profile_pic
            FROM users WHERE id=?
        """, (session["user_id"],)).fetchone()
        conn.close()
    return render_template("index.html", user=user)

# ===================== REGISTER =====================
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid request"}), 400

    name = data["name"].strip()
    email = data["email"].strip().lower()   # 🔑 normalize
    password = data["password"]
    phone = data.get("phone")
    address = data.get("address")

    hashed_pw = generate_password_hash(password)

    conn = get_db_connection()
    try:
        conn.execute("""
            INSERT INTO users (name, email, phone, password, address)
            VALUES (?,?,?,?,?)
        """, (name, email, phone, hashed_pw, address))
        conn.commit()
        return jsonify({"success": True})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Email already exists"}), 409
    finally:
        conn.close()


# ===================== LOGIN =====================
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid request"}), 400

    email = data["email"].strip().lower()
    password = data["password"]

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    ).fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        return jsonify({"success": True})

    return jsonify({"success": False, "message": "Invalid credentials"}), 401

# ===================== LOGOUT =====================
@app.route("/api/logout")
def api_logout():
    session.clear()
    return jsonify({"success": True})


# ===================== CHECK LOGIN =====================
@app.route("/api/check_login")
def check_login():
    return jsonify({
    "logged_in": "user_id" in session,
    "name": session.get("user_name")
})



# ===================== CATEGORIES =====================
@app.route("/api/categories")
def categories():
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM categories").fetchall()
    conn.close()
    return jsonify([dict(d) for d in data])

# ===================== CENTERS =====================
@app.route("/api/centers/<int:category_id>")
def centers(category_id):
    conn = get_db_connection()
    data = conn.execute("""
        SELECT * FROM diagnostic_centers WHERE category_id=?
    """, (category_id,)).fetchall()
    conn.close()
    return jsonify([dict(d) for d in data])

# ===================== CENTER TESTS =====================
@app.route("/api/center_tests/<int:center_id>")
def api_center_tests(center_id):
    conn = get_db_connection()
    data = conn.execute("""
        SELECT
            t.id AS test_id,
            t.test_name,
            ct.price,
            ct.tat_hours,
            d.home_service
        FROM center_tests ct
        JOIN tests t ON t.id = ct.test_id
        JOIN diagnostic_centers d ON d.id = ct.center_id
        WHERE ct.center_id=?
    """, (center_id,)).fetchall()
    conn.close()
    return jsonify([dict(d) for d in data])



# ===================== BOOK  =====================
@app.route("/book")
def book():
    test_id = request.args.get("test_id")
    center_id = request.args.get("center_id")
    test = request.args.get("test")
    center = request.args.get("center")
    home = request.args.get("home", "false")

    if not test_id or not center_id:
        return redirect("/")

    return render_template(
        "book.html",
        test_id=test_id,
        center_id=center_id,
        test=test,
        center=center,
        home=home
    )

# ===================== BOOK APPOINTMENT =====================
@app.route("/api/book_appointment", methods=["POST"])
@login_required_api
def book_appointment():
    data = request.get_json()
    user_id = session["user_id"]
    center_id = data.get("center_id")
    test_id = data.get("test_id")
    appointment_date = data.get("appointment_date")  # format: YYYY-MM-DD
    time_slot = data.get("time_slot")               # format: HH:MM (24hr)
    home_service = data.get("home_service", "No")
    
    # Reminder options (optional, default values)
    reminder_enabled = data.get("reminder_enabled", True)
    reminder_before_minutes = data.get("reminder_before_minutes", 60)  # default 1 hour

    if not all([center_id, test_id, appointment_date, time_slot]):
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    try:
        conn = get_db_connection()
        
        # Validate center and test
        center_exists = conn.execute(
            "SELECT 1 FROM diagnostic_centers WHERE id=?", (center_id,)
        ).fetchone()
        test_exists = conn.execute(
            "SELECT 1 FROM tests WHERE id=?", (test_id,)
        ).fetchone()

        if not center_exists or not test_exists:
            conn.close()
            return jsonify({"success": False, "message": "Invalid center or test ID"}), 400

        # Calculate reminder datetime
        appointment_datetime = datetime.strptime(f"{appointment_date} {time_slot}", "%Y-%m-%d %H:%M")
        reminder_at = (appointment_datetime - timedelta(minutes=reminder_before_minutes)).strftime("%Y-%m-%d %H:%M:%S")


        # Insert booking with reminder fields
        conn.execute("""
            INSERT INTO appointments
            (user_id, center_id, test_id, appointment_date, time_slot, home_service, booking,
             reminder_enabled, reminder_before_minutes, reminder_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, center_id, test_id, appointment_date, time_slot, home_service, "Confirmed",
            int(reminder_enabled), reminder_before_minutes, reminder_at

        ))

        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Appointment booked successfully ✅"})

    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Time slot already booked"}), 409
    except Exception as e:
        print("BOOKING ERROR:", e)
        return jsonify({"success": False, "message": "Server error"}), 500



#====================== My Appointments =====================
@app.route("/api/my-appointments")
def my_appointments():
    if "user_id" not in session:
        return jsonify([])

    user_id = session["user_id"]

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT
            a.id AS appointment_id,
            a.appointment_date,
            a.time_slot,
            a.booking,
            a.reminder_enabled,
            a.reminder_before_minutes,
            t.test_name,
            c.name AS center_name
        FROM appointments a
        JOIN tests t ON t.id = a.test_id
        JOIN diagnostic_centers c ON c.id = a.center_id
        WHERE a.user_id = ?
        ORDER BY a.id DESC
    """, (user_id,))

    rows = cur.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])




# ===================== Appointment Details =====================
@app.route("/api/appointment/<int:appointment_id>")
@login_required_api
def appointment_details(appointment_id):
    user_id = session["user_id"]
    conn = get_db_connection()
    
    row = conn.execute("""
        SELECT
            a.id,
            a.appointment_date,
            a.time_slot,
            a.home_service,
            a.booking,
            t.test_name AS test_name,
            d.name AS center_name,
            d.location AS center_address,
            a.reminder_enabled,
            a.reminder_before_minutes,
            a.reminder_at,
            a.reminder_status
        FROM appointments a
        JOIN tests t ON a.test_id = t.id
        JOIN diagnostic_centers d ON a.center_id = d.id
        WHERE a.id = ? AND a.user_id = ?
    """, (appointment_id, user_id)).fetchone()
    
    conn.close()

    if not row:
        return jsonify({"success": False, "message": "Appointment not found"}), 404

    return jsonify({
        "appointment_id": row["id"],
        "test_name": row["test_name"],
        "center_name": row["center_name"],
        "center_address": row["center_address"],
        "appointment_date": row["appointment_date"],
        "time_slot": row["time_slot"],
        "home_service": row["home_service"],
        "booking": row["booking"],
        "reminder_enabled": bool(row["reminder_enabled"]),
        "reminder_before_minutes": row["reminder_before_minutes"],
        "reminder_at": row["reminder_at"],
        "reminder_status": row["reminder_status"],
    })


# ===================== Cancel Appointment =====================
@app.route("/api/appointment/<int:appointment_id>/cancel", methods=["POST"])
@login_required_api
def cancel_appointment(appointment_id):
    user_id = session["user_id"]
    conn = get_db_connection()

    row = conn.execute("""
        SELECT id FROM appointments
        WHERE id = ? AND user_id = ?
    """, (appointment_id, user_id)).fetchone()

    if not row:
        conn.close()
        return jsonify({"success": False, "message": "Appointment not found"}), 404

    # Update booking status and disable reminder
    conn.execute("""
        UPDATE appointments
        SET booking = 'Cancelled',
            reminder_enabled = 0,
            reminder_status = 'cancelled'
        WHERE id = ? AND user_id = ?
    """, (appointment_id, user_id))
    
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Appointment cancelled ✅, reminder disabled"})

#===================== Notifications api ===========================
@app.route("/api/notifications")
@login_required_api
def api_notifications():
    user_id = session["user_id"]
    conn = get_db_connection()
    notifications = conn.execute(
        "SELECT id, title, message, is_read FROM notifications WHERE user_id=? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return jsonify([dict(n) for n in notifications])


# ===================== RUN =====================
if __name__ == "__main__":
    app.run(debug=True)
