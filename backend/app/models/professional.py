"""
Professional database models for attendance monitoring system.
Optimized for MySQL with proper relationships and indexes.
"""
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, Float, Boolean, ForeignKey, Date, Time, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from app.core.database import Base
import json


class EmployeeStatus(str, Enum):
    """Employee status enum."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"


class AttendanceStatus(str, Enum):
    """Attendance status enum."""
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    HALF_DAY = "half_day"
    ON_LEAVE = "on_leave"


class Department(Base):
    """Department model for organizing employees."""
    
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(20), unique=True, nullable=True, index=True)
    description = Column(Text, nullable=True)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    employees = relationship("Employee", back_populates="department")
    manager = relationship("Employee", foreign_keys=[manager_id])
    
    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}')>"


class Employee(Base):
    """Enhanced employee model with comprehensive information."""
    
    __tablename__ = "employees"
    
    # Basic Information
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    
    # Employment Details
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True, index=True)
    position = Column(String(100), nullable=True)
    hire_date = Column(Date, nullable=True)
    status = Column(SQLEnum(EmployeeStatus), default=EmployeeStatus.ACTIVE)
    
    # Face Recognition Data
    face_embedding = Column(LargeBinary, nullable=True)  # Serialized numpy array
    face_image_path = Column(String(500), nullable=True)  # Reference image
    face_model_version = Column(String(50), default="V1.0")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100), nullable=True)
    
    # Relationships
    department = relationship("Department", back_populates="employees")
    attendance_records = relationship("Attendance", back_populates="employee")
    attendance_sessions = relationship("AttendanceSession", back_populates="employee")
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Employee(id={self.id}, employee_id='{self.employee_id}', name='{self.full_name}')>"


class Attendance(Base):
    """Comprehensive attendance record model."""
    
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    
    # Timing Information
    check_in_time = Column(DateTime, nullable=False, index=True)
    check_out_time = Column(DateTime, nullable=True, index=True)
    break_start_time = Column(DateTime, nullable=True)
    break_end_time = Column(DateTime, nullable=True)
    
    # Duration Calculations
    total_work_hours = Column(Float, default=0.0)  # In hours
    break_hours = Column(Float, default=0.0)  # In hours
    overtime_hours = Column(Float, default=0.0)  # In hours
    
    # Recognition Data
    recognition_confidence = Column(Float, nullable=False)
    check_in_image_path = Column(String(500), nullable=True)
    check_out_image_path = Column(String(500), nullable=True)
    
    # Status and Classification
    status = Column(SQLEnum(AttendanceStatus), default=AttendanceStatus.PRESENT)
    is_late = Column(Boolean, default=False)
    is_early_departure = Column(Boolean, default=False)
    
    # Location Information
    check_in_location = Column(String(200), nullable=True)
    check_out_location = Column(String(200), nullable=True)
    camera_id = Column(String(50), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    # Relationships
    employee = relationship("Employee", back_populates="attendance_records")
    
    def __repr__(self):
        return f"<Attendance(id={self.id}, employee_id={self.employee_id}, date={self.date})>"


class AttendanceSession(Base):
    """Detailed session tracking for continuous monitoring."""
    
    __tablename__ = "attendance_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    session_start = Column(DateTime, nullable=False, index=True)
    session_end = Column(DateTime, nullable=True, index=True)
    
    # Session Data
    duration_minutes = Column(Integer, default=0)
    face_detections = Column(Integer, default=0)
    confidence_avg = Column(Float, default=0.0)
    confidence_min = Column(Float, default=0.0)
    confidence_max = Column(Float, default=0.0)
    
    # Images and Media
    image_count = Column(Integer, default=0)
    first_image_path = Column(String(500), nullable=True)
    last_image_path = Column(String(500), nullable=True)
    
    # Status
    status = Column(String(20), default='active')  # active, completed, interrupted
    end_reason = Column(String(100), nullable=True)  # manual, automatic, error
    
    # Technical Details
    camera_id = Column(String(50), nullable=True)
    processing_time_ms = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee", back_populates="attendance_sessions")
    
    def __repr__(self):
        return f"<AttendanceSession(id={self.id}, employee_id={self.employee_id}, status='{self.status}')>"


class DailyAttendanceSummary(Base):
    """Daily summary for quick reporting and analytics."""
    
    __tablename__ = "daily_attendance_summary"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False, index=True)
    
    # Count Statistics
    total_employees = Column(Integer, default=0)
    employees_present = Column(Integer, default=0)
    employees_absent = Column(Integer, default=0)
    employees_late = Column(Integer, default=0)
    employees_on_leave = Column(Integer, default=0)
    
    # Percentage Calculations
    attendance_rate = Column(Float, default=0.0)
    punctuality_rate = Column(Float, default=0.0)
    
    # Time Statistics
    first_check_in = Column(DateTime, nullable=True)
    last_check_out = Column(DateTime, nullable=True)
    avg_work_hours = Column(Float, default=0.0)
    total_overtime_hours = Column(Float, default=0.0)
    
    # Department-wise breakdown (stored as JSON)
    department_stats = Column(Text, nullable=True)  # JSON string
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_department_stats(self, stats_dict):
        """Store department statistics as JSON."""
        self.department_stats = json.dumps(stats_dict)
    
    def get_department_stats(self):
        """Get department statistics as dictionary."""
        if self.department_stats:
            return json.loads(self.department_stats)
        return {}
    
    def __repr__(self):
        return f"<DailyAttendanceSummary(date={self.date}, rate={self.attendance_rate})>"


class AttendanceSettings(Base):
    """System settings for attendance monitoring."""
    
    __tablename__ = "attendance_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    data_type = Column(String(20), default='string')  # string, integer, float, boolean, json
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<AttendanceSettings(key='{self.key}', value='{self.value}')>"


class AttendanceAlert(Base):
    """Alert and notification system for attendance anomalies."""
    
    __tablename__ = "attendance_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True, index=True)
    alert_type = Column(String(50), nullable=False, index=True)  # absence, late, early_departure, etc.
    severity = Column(String(20), default='medium')  # low, medium, high, critical
    
    # Alert Details
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    date = Column(Date, nullable=False, index=True)
    
    # Status
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(100), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    employee = relationship("Employee")
    
    def __repr__(self):
        return f"<AttendanceAlert(id={self.id}, type='{self.alert_type}', resolved={self.is_resolved})>"


class SystemLog(Base):
    """System activity and error logging."""
    
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_level = Column(String(20), nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    category = Column(String(50), nullable=False, index=True)  # attendance, recognition, system, etc.
    
    # Log Details
    message = Column(Text, nullable=False)
    details = Column(Text, nullable=True)  # JSON string for additional data
    
    # Context Information
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True, index=True)
    session_id = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    employee = relationship("Employee")
    
    def __repr__(self):
        return f"<SystemLog(level='{self.log_level}', category='{self.category}')>"
