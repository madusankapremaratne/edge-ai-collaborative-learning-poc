"""
Database models and session management for Edge AI Collaborative Learning Platform
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import StaticPool
import enum

from config import config

# Create database engine
if config.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        config.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(
        config.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


# Enums
class UserRole(str, enum.Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


class GroupStatus(str, enum.Enum):
    THRIVING = "Thriving"
    HEALTHY = "Healthy"
    AT_RISK = "At Risk"
    CRITICAL = "Critical"


class MilestoneStatus(str, enum.Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    OVERDUE = "Overdue"


class MessageTone(str, enum.Enum):
    SUPPORTIVE = "supportive"
    COLLABORATIVE = "collaborative"
    URGENT = "urgent"
    DIRECT = "direct"
    NEUTRAL = "neutral"


# Database Models
class User(Base):
    """User model for students, instructors, and admins"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.STUDENT)
    is_active = Column(Boolean, default=True)
    lms_user_id = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student_profile = relationship("Student", back_populates="user", uselist=False)
    instructor_profile = relationship("Instructor", back_populates="user", uselist=False)


class Student(Base):
    """Student profile with learning metrics"""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    student_id = Column(String(50), unique=True, index=True)
    current_group_id = Column(Integer, ForeignKey("groups.id"))
    total_hours = Column(Float, default=0.0)
    tasks_completed = Column(Integer, default=0)
    last_activity = Column(DateTime)
    status = Column(String(50), default="Active")
    preferences = Column(JSON)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    group = relationship("Group", back_populates="students")
    contributions = relationship("Contribution", back_populates="student")
    messages = relationship("Communication", back_populates="student")


class Instructor(Base):
    """Instructor profile"""
    __tablename__ = "instructors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    instructor_id = Column(String(50), unique=True, index=True)
    department = Column(String(100))

    # Relationships
    user = relationship("User", back_populates="instructor_profile")
    courses = relationship("Course", back_populates="instructor")


class Course(Base):
    """Course model"""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(50), unique=True, index=True, nullable=False)
    course_name = Column(String(255), nullable=False)
    instructor_id = Column(Integer, ForeignKey("instructors.id"))
    lms_course_id = Column(String(100), unique=True, index=True)
    semester = Column(String(50))
    year = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    instructor = relationship("Instructor", back_populates="courses")
    groups = relationship("Group", back_populates="course")


class Group(Base):
    """Collaborative learning group"""
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    group_name = Column(String(100), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    project_name = Column(String(255))
    status = Column(SQLEnum(GroupStatus), default=GroupStatus.HEALTHY)
    health_score = Column(Float, default=1.0)
    deadline = Column(DateTime)
    lms_group_id = Column(String(100), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="groups")
    students = relationship("Student", back_populates="group")
    milestones = relationship("Milestone", back_populates="group")
    communications = relationship("Communication", back_populates="group")
    health_records = relationship("GroupHealthRecord", back_populates="group")


class Contribution(Base):
    """Student contribution tracking"""
    __tablename__ = "contributions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    task_type = Column(String(100), nullable=False)
    action = Column(Text, nullable=False)
    hours = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    lms_activity_id = Column(String(100), index=True)
    metadata = Column(JSON)

    # Relationships
    student = relationship("Student", back_populates="contributions")


class Milestone(Base):
    """Project milestones"""
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(MilestoneStatus), default=MilestoneStatus.NOT_STARTED)
    due_date = Column(DateTime)
    completed_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    group = relationship("Group", back_populates="milestones")


class Communication(Base):
    """Group communication messages"""
    __tablename__ = "communications"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    message = Column(Text, nullable=False)
    tone = Column(SQLEnum(MessageTone), default=MessageTone.NEUTRAL)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    lms_message_id = Column(String(100), index=True)

    # Relationships
    group = relationship("Group", back_populates="communications")
    student = relationship("Student", back_populates="messages")


class GroupHealthRecord(Base):
    """Historical group health metrics"""
    __tablename__ = "group_health_records"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    health_score = Column(Float, nullable=False)
    participation_imbalance = Column(Float)
    inactive_members_count = Column(Integer, default=0)
    overdue_milestones_count = Column(Integer, default=0)
    issues_detected = Column(JSON)
    recommendations = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    group = relationship("Group", back_populates="health_records")


class AIAgentLog(Base):
    """Logging for AI agent actions and decisions"""
    __tablename__ = "ai_agent_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_type = Column(String(50), nullable=False)  # personal, group, instructor
    agent_id = Column(String(100), index=True)
    action = Column(String(100), nullable=False)
    input_data = Column(JSON)
    output_data = Column(JSON)
    model_used = Column(String(100))
    execution_time_ms = Column(Float)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class AuditLog(Base):
    """Audit log for compliance (FERPA)"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


# Database utility functions
def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")


def drop_db():
    """Drop all tables - use with caution!"""
    Base.metadata.drop_all(bind=engine)
    print("Database dropped successfully")


def reset_db():
    """Reset database - drop and recreate all tables"""
    drop_db()
    init_db()
    print("Database reset successfully")


if __name__ == "__main__":
    # Initialize database when run directly
    init_db()
