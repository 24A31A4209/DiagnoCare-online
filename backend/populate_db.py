import sqlite3
import random
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")


# ================= CONNECT TO DATABASE =================
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

# ================= DROP TABLES (DEV SAFE) =================
cursor.executescript("""
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS center_filters;
DROP TABLE IF EXISTS center_tests;
DROP TABLE IF EXISTS tests;
DROP TABLE IF EXISTS diagnostic_centers;
DROP TABLE IF EXISTS categories;
""")

# ================= CREATE TABLES =================

cursor.execute("""
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
""")

cursor.execute("""
CREATE TABLE diagnostic_centers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    location TEXT,
    rating REAL,
    years_experience INTEGER,
    home_service TEXT,
    insurance_support TEXT,
    UNIQUE(name, category_id),
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
)
""")

cursor.execute("""
CREATE TABLE tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    UNIQUE(test_name, category_id),
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
)
""")

cursor.execute("""
CREATE TABLE center_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    center_id INTEGER NOT NULL,
    test_id INTEGER NOT NULL,
    price INTEGER,
    tat_hours INTEGER,
    UNIQUE(center_id, test_id),
    FOREIGN KEY (center_id) REFERENCES diagnostic_centers(id) ON DELETE CASCADE,
    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE
)
""")

cursor.execute("""
CREATE TABLE center_filters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    center_id INTEGER UNIQUE,
    accreditation TEXT,
    equipment_quality TEXT,
    time_slots TEXT,
    digital_reports TEXT,
    FOREIGN KEY (center_id) REFERENCES diagnostic_centers(id) ON DELETE CASCADE
)
""")

cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    password TEXT NOT NULL,
    address TEXT,
    profile_pic TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute(""" 
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    center_id INTEGER NOT NULL,
    test_id INTEGER NOT NULL,
    appointment_date TEXT NOT NULL,
    time_slot TEXT NOT NULL,
    home_service TEXT,
    booking TEXT DEFAULT 'Confirmed',   -- booking status
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
               
    -- REMINDER COLUMNS (for on-site notifications only)
    reminder_enabled INTEGER DEFAULT 0,
    reminder_before_minutes INTEGER DEFAULT 60,
    appointment_datetime DATETIME,  -- optional for easier queries
    reminder_at DATETIME,
    reminder_status TEXT DEFAULT 'pending',
    reminder_sent_at DATETIME,
    reminder_error TEXT,

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (center_id) REFERENCES diagnostic_centers(id),
    FOREIGN KEY (test_id) REFERENCES tests(id),

    UNIQUE(center_id, appointment_date, time_slot)
);
""")

# ================= create notifications table =================
cursor.execute(""" 
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT DEFAULT 'reminder',
    is_read INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

""")


# ================= DATASETS =================

# ------------------- Categories -------------------
categories = [
    "Pathology Labs",
    "Radiology",
    "Cardiology Diagnostic Centers",
    "Neurology Diagnostic Centers",
    "Gastroenterology Diagnostic Centers",
    "Urology Diagnostic Centers",
    "Endocrinology Diagnostic Centers",
    "Pulmonology Diagnostic Centers",
    "Dermatology Diagnostic Labs",
    "ENT Diagnostic Centers",
    "Ophthalmology Diagnostic Centers",
    "Orthopedic Diagnostic Centers",
    "Obstetric Diagnostic Centers",
    "Cancer Diagnostic Centers",
    "Dental Diagnostic Centers",
    "Genetic Diagnostic Labs",
    "Wellness & Health Checkup Centers"
]

#================= insert categories =================

for c in categories:
    cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (c,))


cursor.execute("SELECT id, name FROM categories")
category_map = {name: cid for cid, name in cursor.fetchall()}

 #-----------------Centres data---------------

centers_data = {
    "Pathology Labs": [
        ("City Path Labs", "Visakhapatnam", 4.5, 10, "Blood,Urine", "Yes"),
        ("HealthCheck Pathology", "Tirupati", 4.2, 8, "Blood", "Yes"),
        ("MediLab Diagnostics", "Amaravati", 4.0, 5, "Blood,Urine", "No")
    ],
    "Radiology": [
        ("ScanPro Imaging", "Rajahmundry", 4.7, 12, "X-Ray,MRI", "No"),
        ("Imaging Plus", "Anantapur", 4.4, 8, "CT,Ultrasound", "Yes"),
        ("Radiant Scan Center", "Guntur", 4.3, 6, "X-Ray,MRI", "No")
    ],
    "Cardiology Diagnostic Centers": [
        ("HeartCare Center", "Hyderabad", 4.6, 15, "ECG,2D Echo,TMT", "Yes"),
        ("CardioPlus", "Rajahmundry", 4.3, 10, "Holter Monitoring,ECG", "Yes"),
        ("HeartLine Diagnostics", "Hyderabad", 4.1, 7, "ECG,TMT", "No")
    ],
    "Neurology Diagnostic Centers": [
        ("NeuroLabs", "Hyderabad", 4.5, 12, "EEG,EMG,NCS", "No"),
        ("BrainScan Center", "Anantapur", 4.2, 9, "EEG,NCS", "No"),
        ("NeuroCare Diagnostics", "Banglore", 4.0, 7, "EEG,EMG", "Yes")
    ],
    "Gastroenterology Diagnostic Centers": [
        ("GastroHealth", "Tirupati", 4.5, 10, "Endoscopy,Colonoscopy", "No"),
        ("DigestiveCare", "Visakhapatnam", 4.3, 8, "Colonoscopy", "Yes"),
        ("GI Labs", "Guntur", 4.0, 6, "Endoscopy", "No")
    ],
    "Urology Diagnostic Centers": [
        ("UroCheck", "Amaravati", 4.4, 12, "KUB Ultrasound,Prostate Scan", "Yes"),
        ("KidneyCare Labs", "Nellore", 4.2, 8, "Uroflowmetry", "No"),
        ("UroPlus Diagnostics", "Vijayawada", 4.0, 6, "KUB Ultrasound", "Yes")
    ],
    "Endocrinology Diagnostic Centers": [
        ("EndoLabs", "Secunderabad", 4.5, 10, "Thyroid,Insulin,Cortisol", "Yes"),
        ("HormoneCheck", "Guntur", 4.2, 8, "PCOD/PCOS Panels", "No"),
        ("EndoPlus Diagnostics", "Anantapur", 4.0, 6, "Thyroid,Cortisol", "Yes")
    ],
    "Pulmonology Diagnostic Centers": [
        ("LungCare Labs", "Rajahmundry", 4.5, 12, "PFT,Spirometry,Chest X-Ray", "Yes"),
        ("PulmoHealth", "Vijayanagaram", 4.3, 9, "Chest X-Ray,Spirometry", "No"),
        ("Respira Diagnostics", "Secunderabad", 4.0, 7, "PFT", "Yes")
    ],
    "Dermatology Diagnostic Labs": [
        ("SkinCheck Labs", "Eluru", 4.5, 10, "Skin Biopsy,Allergy Patch", "No"),
        ("DermaCare", "Tirupati", 4.3, 8, "Skin Tests", "Yes"),
        ("SkinPlus Diagnostics", "Visakhapatnam", 4.0, 6, "Allergy Patch", "Yes")
    ],
    "ENT Diagnostic Centers": [
        ("ENT Health Labs", "Nellore", 4.5, 12, "Audiometry,Tympanometry,Nasal Endoscopy", "No"),
        ("EarCare Diagnostics", "Amaravati", 4.2, 9, "Hearing Test", "Yes"),
        ("ENTPlus Center", "Eluru", 4.0, 7, "Audiometry", "No")
    ],
    "Ophthalmology Diagnostic Centers": [
        ("EyeCare Labs", "Kurnool", 4.6, 10, "Vision Tests,OCT,Retina Scan,Glaucoma", "No"),
        ("VisionPlus", "Rajahmundry", 4.3, 8, "OCT,Retina Scan", "Yes"),
        ("OptiHealth Diagnostics", "Tirupati", 4.0, 6, "Vision Tests", "Yes")
    ],
    "Orthopedic Diagnostic Centers": [
        ("BoneHealth Labs", "Vijayawada", 4.5, 12, "DEXA,Joint X-Ray", "No"),
        ("OrthoCare", "Nellore", 4.2, 8, "Bone Density Scan", "Yes"),
        ("OrthoPlus Diagnostics", "Guntur", 4.0, 6, "Joint X-Ray", "Yes")
    ],
    "Obstetric Diagnostic Centers": [
        ("Maternity Care Labs", "Amaravati", 4.5, 10, "NT Scan,Anomaly Scan,Fetal Growth Scan", "Yes"),
        ("Prenatal Diagnostics", "Rajahmundry", 4.2, 8, "NT Scan,Fetal Growth", "Yes"),
        ("BabyCheck Labs", "Chittoor", 4.0, 6, "Anomaly Scan", "No")
    ],
    "Cancer Diagnostic Centers": [
        ("CancerCare Labs", "Kurnool", 4.6, 12, "Biopsy,Tumor Markers,PET-CT", "No"),
        ("OncoPlus Diagnostics", "Hyderabad", 4.3, 9, "Biopsy,CA-125,PSA", "Yes"),
        ("OncoHealth Labs", "Rajahmundry", 4.0, 7, "AFP,PET-CT", "Yes")
    ],
    "Dental Diagnostic Centers": [
        ("DentalCheck Labs", "Kurnool", 4.5, 10, "OPG,CBCT", "No"),
        ("SmilePlus", "Vijayawada", 4.3, 8, "CBCT", "Yes"),
        ("TeethCare Diagnostics", "Tirupati", 4.0, 6, "OPG", "No")
    ],
    "Genetic Diagnostic Labs": [
        ("GeneLabs", "Guntur", 4.5, 12, "DNA,Karyotyping,Genetic Mutation", "Yes"),
        ("GeneticPlus", "Amaravati", 4.2, 9, "Karyotyping,DNA Test", "No"),
        ("GeneHealth Diagnostics", "Nellore", 4.0, 7, "Genetic Mutation Test", "Yes")
    ],
    "Wellness & Health Checkup Centers": [
        ("Wellness Health", "Kurnool", 4.6, 15, "Full-body,Basic,Executive,Women,Senior", "Yes"),
        ("CheckupPlus", "Rajahmundry", 4.3, 12, "Basic,Executive", "No"),
        ("HealthCheckup Labs", "Vijayawada", 4.0, 10, "Women,Senior", "Yes")
    ]
}

# ================= INSERT CENTERS =================
center_ids = {}

for category, centers in centers_data.items():
    for c in centers:
        cursor.execute("""
        INSERT INTO diagnostic_centers
        (name, category_id, location, rating, years_experience, home_service, insurance_support)
        VALUES (?,?,?,?,?,?,?)
        """, (c[0], category_map[category], c[1], c[2], c[3], c[4], c[5]))
        center_ids[c[0]] = cursor.lastrowid


#-----------------Tests data---------------

tests_data = {
    "Pathology Labs": ["CBC", "Thyroid", "Diabetes", "Lipid Profile", "Liver/Kidney Tests"],
    "Radiology": ["X-Ray", "MRI", "CT Scan", "Ultrasound", "Mammography", "PET Scan"],
    "Cardiology Diagnostic Centers": ["ECG", "2D Echo", "TMT", "Holter Monitoring"],
    "Neurology Diagnostic Centers": ["EEG", "EMG", "NCS"],
    "Gastroenterology Diagnostic Centers": ["Endoscopy", "Colonoscopy"],
    "Urology Diagnostic Centers": ["KUB Ultrasound", "Prostate Scan", "Uroflowmetry"],
    "Endocrinology Diagnostic Centers": ["Thyroid", "Insulin", "Cortisol", "PCOD/PCOS Panels"],
    "Pulmonology Diagnostic Centers": ["PFT", "Spirometry", "Chest X-ray"],
    "Dermatology Diagnostic Labs": ["Skin Biopsy", "Allergy Patch Testing"],
    "ENT Diagnostic Centers": ["Audiometry", "Tympanometry", "Nasal Endoscopy"],
    "Ophthalmology Diagnostic Centers": ["Vision Tests", "OCT", "Retina Scan", "Glaucoma Tests"],
    "Orthopedic Diagnostic Centers": ["DEXA", "Joint X-ray"],
    "Obstetric Diagnostic Centers": ["NT Scan", "Anomaly Scan", "Fetal Growth Scan"],
    "Cancer Diagnostic Centers": ["Biopsy", "Tumor Markers", "PET-CT"],
    "Dental Diagnostic Centers": ["OPG", "CBCT"],
    "Genetic Diagnostic Labs": ["DNA Test", "Karyotyping", "Genetic Mutation Test"],
    "Wellness & Health Checkup Centers": ["Full-body", "Basic", "Executive", "Women", "Senior"]
}


# ================= INSERT TESTS =================
test_ids = {}
for category, tests in tests_data.items():
    for t in tests:
        cursor.execute(
            "INSERT INTO tests (test_name, category_id) VALUES (?,?)",
            (t, category_map[category])
        )
        test_ids[(category, t)] = cursor.lastrowid

# ================= CENTER–TEST MAPPING =================
for category, centers in centers_data.items():
    for c in centers:
        for t in tests_data[category]:
            cursor.execute("""
            INSERT INTO center_tests (center_id, test_id, price, tat_hours)
            VALUES (?,?,?,?)
            """, (
                center_ids[c[0]],
                test_ids[(category, t)],
                random.randint(300, 5000),
                random.choice([24, 48, 72])
            ))

# ================= CENTER FILTERS =================
for cid in center_ids.values():
    cursor.execute("""
    INSERT INTO center_filters
    (center_id, accreditation, equipment_quality, time_slots, digital_reports)
    VALUES (?,?,?,?,?)
    """, (
        cid,
        random.choice(["NABL","ISO Certified"]),
        random.choice(["High-End","Standard"]),
        random.choice(["Morning","Afternoon","Evening"]),
        random.choice(["Yes","No"])
    ))

# ================================
# CREATE INDEXES (REMINDER FEATURE)
# ================================

cursor.execute(
    "CREATE INDEX IF NOT EXISTS idx_appointments_reminder_at ON appointments(reminder_at)"
)

cursor.execute(
    "CREATE INDEX IF NOT EXISTS idx_appointments_reminder_status ON appointments(reminder_status)"
)

cursor.execute(
    "CREATE INDEX IF NOT EXISTS idx_appointments_user_id ON appointments(user_id)"
)

cursor.execute(
    "CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)"
)

cursor.execute(
    "CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read)"
)


# ================= COMMIT =================
conn.commit()
conn.close()

print("✅ FULL DATABASE CREATED SUCCESSFULLY")
