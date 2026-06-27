"""
Enhanced database models for attendance tracking.
"""
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, Float, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Person(Base):
    """Person model to store face embeddings and basic info."""
    
    __tablename__ = "persons"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    department = Column(String(100), nullable=True)
    person_code = Column(String(50), unique=True, nullable=True)  # student_id / employee_id
    person_type = Column(String(20), default="student", nullable=False)  # student | staff
    embedding = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    attendance_records = relationship("Attendance", back_populates="person")
    
    def __repr__(self):
        return f"<Person(id={self.id}, name='{self.name}', type='{self.person_type}')>"


class Attendance(Base):
    """Attendance model for tracking person check-ins/check-outs."""
    
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)  # Attendance date
    check_in_time = Column(DateTime, nullable=False)  # First detection time
    check_out_time = Column(DateTime, nullable=True)  # Last detection time
    confidence = Column(Float, nullable=False)  # Recognition confidence
    image_path = Column(String(500), nullable=True)  # Path to attendance image
    total_detections = Column(Integer, default=1)  # Number of times detected
    duration_minutes = Column(Integer, nullable=True)  # Time spent in minutes
    
    # Relationship with person
    person = relationship("Person", back_populates="attendance_records")
    
    def __repr__(self):
        return f"<Attendance(id={self.id}, person_id={self.person_id}, date={self.date})>"


class AttendanceSession(Base):
    """Detailed session tracking for continuous monitoring."""
    
    __tablename__ = "attendance_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    session_start = Column(DateTime, nullable=False)
    session_end = Column(DateTime, nullable=True)
    confidence = Column(Float, nullable=False)
    image_count = Column(Integer, default=0)  # Number of images captured
    status = Column(String(20), default="active")  # active, completed, interrupted
    
    # Relationship with person
    person = relationship("Person")
    
    def __repr__(self):
        return f"<AttendanceSession(id={self.id}, person_id={self.person_id}, status='{self.status}')>"


class DailyAttendanceSummary(Base):
    """Daily summary for quick reporting."""
    
    __tablename__ = "daily_attendance_summary"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False, index=True)
    total_persons_present = Column(Integer, default=0)
    total_persons_expected = Column(Integer, default=0)
    attendance_rate = Column(Float, default=0.0)
    first_check_in = Column(DateTime, nullable=True)
    last_check_out = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<DailyAttendanceSummary(date={self.date}, rate={self.attendance_rate})>"
