"""
Tests for authentication and authorization
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, User, UserRole
from auth import AuthService


@pytest.fixture
def db_session():
    """Create a test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSessionLocal = sessionmaker(bind=engine)
    session = TestSessionLocal()
    yield session
    session.close()


@pytest.fixture
def auth_service():
    """Create an auth service instance"""
    return AuthService()


def test_password_hashing(auth_service):
    """Test password hashing and verification"""
    password = "test_password_123"
    hashed = auth_service.hash_password(password)

    assert hashed != password
    assert auth_service.verify_password(password, hashed)
    assert not auth_service.verify_password("wrong_password", hashed)


def test_create_user(auth_service, db_session):
    """Test user creation"""
    user = auth_service.create_user(
        username="testuser",
        email="test@example.com",
        password="password123",
        full_name="Test User",
        role=UserRole.STUDENT,
        db=db_session
    )

    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.role == UserRole.STUDENT
    assert user.is_active


def test_create_duplicate_user(auth_service, db_session):
    """Test that duplicate users cannot be created"""
    auth_service.create_user(
        username="testuser",
        email="test@example.com",
        password="password123",
        full_name="Test User",
        role=UserRole.STUDENT,
        db=db_session
    )

    # Try to create duplicate
    duplicate = auth_service.create_user(
        username="testuser",
        email="different@example.com",
        password="password123",
        full_name="Test User 2",
        role=UserRole.STUDENT,
        db=db_session
    )

    assert duplicate is None


def test_authenticate_user(auth_service, db_session):
    """Test user authentication"""
    # Create user
    auth_service.create_user(
        username="testuser",
        email="test@example.com",
        password="password123",
        full_name="Test User",
        role=UserRole.STUDENT,
        db=db_session
    )

    # Test successful authentication
    user = auth_service.authenticate_user("testuser", "password123", db_session)
    assert user is not None
    assert user.username == "testuser"

    # Test failed authentication
    failed = auth_service.authenticate_user("testuser", "wrongpassword", db_session)
    assert failed is None


def test_create_access_token(auth_service):
    """Test JWT token creation"""
    token = auth_service.create_access_token(
        user_id=1,
        username="testuser",
        role=UserRole.STUDENT
    )

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_token(auth_service):
    """Test JWT token decoding"""
    token = auth_service.create_access_token(
        user_id=1,
        username="testuser",
        role=UserRole.STUDENT
    )

    payload = auth_service.decode_token(token)
    assert payload is not None
    assert payload["sub"] == "1"
    assert payload["username"] == "testuser"
    assert payload["role"] == "student"


def test_decode_invalid_token(auth_service):
    """Test decoding invalid token"""
    payload = auth_service.decode_token("invalid_token")
    assert payload is None


def test_check_permission(auth_service, db_session):
    """Test permission checking"""
    # Create users with different roles
    student = auth_service.create_user(
        username="student",
        email="student@example.com",
        password="pass",
        full_name="Student",
        role=UserRole.STUDENT,
        db=db_session
    )

    instructor = auth_service.create_user(
        username="instructor",
        email="instructor@example.com",
        password="pass",
        full_name="Instructor",
        role=UserRole.INSTRUCTOR,
        db=db_session
    )

    admin = auth_service.create_user(
        username="admin",
        email="admin@example.com",
        password="pass",
        full_name="Admin",
        role=UserRole.ADMIN,
        db=db_session
    )

    # Test student permissions
    assert auth_service.check_permission(student, UserRole.STUDENT)
    assert not auth_service.check_permission(student, UserRole.INSTRUCTOR)
    assert not auth_service.check_permission(student, UserRole.ADMIN)

    # Test instructor permissions
    assert auth_service.check_permission(instructor, UserRole.STUDENT)
    assert auth_service.check_permission(instructor, UserRole.INSTRUCTOR)
    assert not auth_service.check_permission(instructor, UserRole.ADMIN)

    # Test admin permissions
    assert auth_service.check_permission(admin, UserRole.STUDENT)
    assert auth_service.check_permission(admin, UserRole.INSTRUCTOR)
    assert auth_service.check_permission(admin, UserRole.ADMIN)
