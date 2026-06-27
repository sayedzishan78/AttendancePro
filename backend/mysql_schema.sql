-- Attendance Monitoring System - MySQL Schema
-- Compatible with MySQL 8.0+ and MySQL Workbench

CREATE DATABASE IF NOT EXISTS attendance_system
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE attendance_system;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS admin_users;
DROP TABLE IF EXISTS daily_attendance_summary;
DROP TABLE IF EXISTS attendance_sessions;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS persons;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE persons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    department VARCHAR(100),
    person_code VARCHAR(50) UNIQUE,
    person_type VARCHAR(20) DEFAULT 'student' NOT NULL,
    embedding LONGBLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB;

CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT NOT NULL,
    date DATE NOT NULL,
    check_in_time TIMESTAMP NOT NULL,
    check_out_time TIMESTAMP NULL,
    confidence DECIMAL(5,4) NOT NULL,
    image_path VARCHAR(500),
    total_detections INT DEFAULT 1,
    duration_minutes INT,
    INDEX idx_attendance_person_date (person_id, date),
    FOREIGN KEY (person_id) REFERENCES persons(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE attendance_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT NOT NULL,
    session_start TIMESTAMP NOT NULL,
    session_end TIMESTAMP NULL,
    confidence DECIMAL(5,4) NOT NULL,
    image_count INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    INDEX idx_sessions_person_start (person_id, session_start),
    FOREIGN KEY (person_id) REFERENCES persons(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE daily_attendance_summary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    total_persons_present INT DEFAULT 0,
    total_persons_expected INT DEFAULT 0,
    attendance_rate DECIMAL(5,2) DEFAULT 0.00,
    first_check_in TIMESTAMP NULL,
    last_check_out TIMESTAMP NULL,
    INDEX idx_summary_date (date)
) ENGINE=InnoDB;

CREATE TABLE admin_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB;

SELECT 'Database schema created successfully!' as status;
