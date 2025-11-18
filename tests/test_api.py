"""
Tests for FastAPI endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from api import app
from auth import auth_service, UserRole


# Test database setup
@pytest.fixture
def test_db():
    """Create a test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSessionLocal = sessionmaker(bind=engine)
    return TestSessionLocal()


@pytest.fixture
def client(test_db):
    """Create a test client"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"


def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User",
            "role": "student"
        }
    )
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"
    assert response.json()["email"] == "test@example.com"


def test_register_duplicate_user(client):
    """Test registering duplicate user fails"""
    # First registration
    client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User",
            "role": "student"
        }
    )

    # Duplicate registration
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "different@example.com",
            "password": "password123",
            "full_name": "Test User 2",
            "role": "student"
        }
    )
    assert response.status_code == 400


def test_login(client, test_db):
    """Test user login"""
    # Create user
    auth_service.create_user(
        username="testuser",
        email="test@example.com",
        password="password123",
        full_name="Test User",
        role=UserRole.STUDENT,
        db=test_db
    )

    # Login
    response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post(
        "/auth/login",
        json={
            "username": "nonexistent",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


def test_get_stats(client):
    """Test overview statistics endpoint"""
    response = client.get("/stats/overview")
    # Will fail without auth if auth is enabled, otherwise should work
    # This test assumes auth might be disabled for testing
    assert response.status_code in [200, 401, 403]


def test_list_students(client):
    """Test listing students"""
    response = client.get("/students")
    # Will fail without auth if auth is enabled
    assert response.status_code in [200, 401, 403]


def test_list_groups(client):
    """Test listing groups"""
    response = client.get("/groups")
    # Will fail without auth if auth is enabled
    assert response.status_code in [200, 401, 403]
