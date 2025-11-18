"""
Authentication and Authorization for Edge AI Collaborative Learning Platform
Implements JWT-based authentication and RBAC
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError

from config import config
from database import User, UserRole, Session, SessionLocal

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication and authorization service"""

    def __init__(self):
        self.secret_key = config.JWT_SECRET_KEY
        self.algorithm = config.JWT_ALGORITHM
        self.expiration_hours = config.JWT_EXPIRATION_HOURS

    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(
        self,
        user_id: int,
        username: str,
        role: UserRole,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=self.expiration_hours)

        payload = {
            "sub": str(user_id),
            "username": username,
            "role": role.value if isinstance(role, UserRole) else role,
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate a JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error decoding token: {e}")
            return None

    def authenticate_user(self, username: str, password: str, db: Session) -> Optional[User]:
        """Authenticate a user with username and password"""
        try:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                logger.warning(f"Authentication failed: user '{username}' not found")
                return None

            if not user.is_active:
                logger.warning(f"Authentication failed: user '{username}' is inactive")
                return None

            if not self.verify_password(password, user.hashed_password):
                logger.warning(f"Authentication failed: invalid password for user '{username}'")
                return None

            logger.info(f"User '{username}' authenticated successfully")
            return user

        except Exception as e:
            logger.error(f"Error during authentication: {e}")
            return None

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str,
        role: UserRole,
        db: Session
    ) -> Optional[User]:
        """Create a new user"""
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()

            if existing_user:
                logger.warning(f"User creation failed: username or email already exists")
                return None

            # Create new user
            hashed_password = self.hash_password(password)
            user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                full_name=full_name,
                role=role,
                is_active=True
            )

            db.add(user)
            db.commit()
            db.refresh(user)

            logger.info(f"User '{username}' created successfully with role '{role.value}'")
            return user

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {e}")
            return None

    def get_current_user(self, token: str, db: Session) -> Optional[User]:
        """Get current user from JWT token"""
        payload = self.decode_token(token)
        if not payload:
            return None

        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()

        if not user or not user.is_active:
            return None

        return user

    def check_permission(
        self,
        user: User,
        required_role: UserRole
    ) -> bool:
        """Check if user has required role or higher"""
        role_hierarchy = {
            UserRole.STUDENT: 1,
            UserRole.INSTRUCTOR: 2,
            UserRole.ADMIN: 3,
        }

        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        return user_level >= required_level

    def check_resource_access(
        self,
        user: User,
        resource_type: str,
        resource_id: int,
        db: Session
    ) -> bool:
        """Check if user has access to a specific resource"""
        # Admins have access to everything
        if user.role == UserRole.ADMIN:
            return True

        # Students can access their own data
        if user.role == UserRole.STUDENT and resource_type == "student":
            student = db.query(User).filter(User.id == resource_id).first()
            return student and student.id == user.id

        # Instructors can access their courses and groups
        if user.role == UserRole.INSTRUCTOR and resource_type in ["course", "group"]:
            # This would require more complex logic based on course ownership
            # For now, allow all instructors to access all courses/groups
            return True

        return False


class AuthMiddleware:
    """Middleware for authentication in web frameworks"""

    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    def extract_token_from_header(self, authorization: str) -> Optional[str]:
        """Extract JWT token from Authorization header"""
        if not authorization:
            return None

        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        return parts[1]

    def authenticate_request(self, authorization: str, db: Session) -> Optional[User]:
        """Authenticate a request using Authorization header"""
        token = self.extract_token_from_header(authorization)
        if not token:
            return None

        return self.auth_service.get_current_user(token, db)


# Singleton instances
auth_service = AuthService()
auth_middleware = AuthMiddleware(auth_service)


# Utility functions for common operations
def create_default_admin(db: Session) -> Optional[User]:
    """Create default admin user for initial setup"""
    return auth_service.create_user(
        username="admin",
        email="admin@example.com",
        password="admin123",  # Should be changed immediately
        full_name="System Administrator",
        role=UserRole.ADMIN,
        db=db
    )


def login_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Login user and return token"""
    db = SessionLocal()
    try:
        user = auth_service.authenticate_user(username, password, db)
        if not user:
            return None

        token = auth_service.create_access_token(
            user_id=user.id,
            username=user.username,
            role=user.role
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value
            }
        }
    finally:
        db.close()


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a JWT token and return payload"""
    return auth_service.decode_token(token)


if __name__ == "__main__":
    # Test authentication
    from database import init_db

    init_db()
    db = SessionLocal()

    try:
        # Create test admin user
        admin = create_default_admin(db)
        if admin:
            print(f"Admin user created: {admin.username}")

            # Test login
            result = login_user("admin", "admin123")
            if result:
                print(f"Login successful. Token: {result['access_token'][:50]}...")

                # Verify token
                payload = verify_token(result['access_token'])
                print(f"Token verified. User: {payload.get('username')}, Role: {payload.get('role')}")
        else:
            print("Admin user already exists")

    finally:
        db.close()
