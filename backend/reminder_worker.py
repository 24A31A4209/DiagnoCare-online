# reminder_worker.py
import sqlite3
import time
from datetime import datetime
import os

# ---------------- CONFIGURATION ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
CHECK_INTERVAL = 60  # seconds between checks

# ---------------- HELPER FUNCTIONS ----------------
def create_notification(cursor, user_id, title, message):
    """
    Create an in-site notification for the user.
    """
    cursor.execute(
        """
        INSERT INTO notifications (user_id, title, message)
        VALUES (?, ?, ?)
        """,
        (user_id, title, message)
    )

# ---------------- REMINDER PROCESSING ----------------
def process_reminders():
    """
    Check appointments for pending reminders and process them.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # ensure format matches SQLite
    
    # Select appointments needing reminders
    cursor.execute("""
        SELECT a.id, a.user_id, a.reminder_status, u.name, t.test_name, c.name
        FROM appointments a
        JOIN users u ON u.id = a.user_id
        JOIN tests t ON t.id = a.test_id
        JOIN diagnostic_centers c ON c.id = a.center_id
        WHERE a.reminder_enabled = 1
          AND a.reminder_status = 'pending'
          AND a.reminder_at IS NOT NULL
          AND a.reminder_at <= ?
    """, (now,))
    
    reminders = cursor.fetchall()
    
    for appt in reminders:
        try:
            appt_id, user_id, reminder_status, name, test_name, center_name = appt
            
            message = f"Hello {name}, your test '{test_name}' at '{center_name}' is coming up soon!"
            
            # Mark reminder as sent
            cursor.execute("""
                UPDATE appointments
                SET reminder_status='sent', reminder_sent_at=?
                WHERE id=?
            """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), appt_id))
            
            # Create an in-site notification
            create_notification(cursor, user_id, "Appointment Reminder", message)
            
            print(f"✅ Reminder processed for appointment ID {appt_id}")
        except Exception as e:
            print(f"❌ Failed to process reminder for appointment ID {appt[0]}:", e)
    
    conn.commit()
    conn.close()

# ---------------- MAIN LOOP ----------------
if __name__ == "__main__":
    print("🕒 Reminder worker started...")
    while True:
        try:
            process_reminders()
        except Exception as e:
            print("❌ Error processing reminders:", e)
        time.sleep(CHECK_INTERVAL)
