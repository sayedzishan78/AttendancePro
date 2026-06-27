-- Core SQL Schema for Attendance System
-- Compatible with SQLite/MySQL with minor adjustments

DROP TABLE IF EXISTS admin_users;
DROP TABLE IF EXISTS daily_attendance_summary;
DROP TABLE IF EXISTS attendance_sessions;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS persons;

CREATE TABLE persons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    department VARCHAR(100),
    person_code VARCHAR(50) UNIQUE,
    person_type VARCHAR(20) DEFAULT 'student' NOT NULL,
    embedding BLOB NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    date DATE NOT NULL,
    check_in_time DATETIME NOT NULL,
    check_out_time DATETIME,
    confidence REAL NOT NULL,
    image_path VARCHAR(500),
    total_detections INTEGER DEFAULT 1,
    duration_minutes INTEGER,
    FOREIGN KEY (person_id) REFERENCES persons(id) ON DELETE CASCADE
);

CREATE TABLE attendance_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL,
    session_start DATETIME NOT NULL,
    session_end DATETIME,
    confidence REAL NOT NULL,
    image_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    FOREIGN KEY (person_id) REFERENCES persons(id) ON DELETE CASCADE
);

CREATE TABLE daily_attendance_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE UNIQUE NOT NULL,
    total_persons_present INTEGER DEFAULT 0,
    total_persons_expected INTEGER DEFAULT 0,
    attendance_rate REAL DEFAULT 0.0,
    first_check_in DATETIME,
    last_check_out DATETIME
);

CREATE TABLE admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
