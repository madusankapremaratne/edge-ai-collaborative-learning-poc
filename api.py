"""
REST API for Edge AI Collaborative Learning Platform
FastAPI-based API with authentication, CRUD operations, and AI agent endpoints
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from config import config
from database import (
    get_db,
    User,
    Student,
    Instructor,
    Group,
    Course,
    Contribution,
    Milestone,
    Communication,
    UserRole,
    GroupStatus,
    MilestoneStatus,
)
from auth import auth_service, auth_middleware
from llm_integration import llm_service

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Edge AI Collaborative Learning API",
    description="REST API for AI-powered collaborative learning platform",
    version="1.0.0",
    docs_url="/docs" if config.ENABLE_SWAGGER_UI else None,
    redoc_url="/redoc" if config.ENABLE_SWAGGER_UI else None,
)

# CORS middleware
if config.ENABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Security
security = HTTPBearer()


# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: str = "student"


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class StudentCreate(BaseModel):
    student_id: str
    user_id: int


class StudentResponse(BaseModel):
    id: int
    student_id: str
    total_hours: float
    tasks_completed: int
    last_activity: Optional[datetime]
    status: str

    class Config:
        from_attributes = True


class GroupCreate(BaseModel):
    group_name: str
    course_id: int
    project_name: str
    deadline: Optional[datetime]


class GroupResponse(BaseModel):
    id: int
    group_name: str
    project_name: Optional[str]
    status: str
    health_score: float
    deadline: Optional[datetime]

    class Config:
        from_attributes = True


class ContributionCreate(BaseModel):
    student_id: int
    task_type: str
    action: str
    hours: float


class ContributionResponse(BaseModel):
    id: int
    task_type: str
    action: str
    hours: float
    timestamp: datetime

    class Config:
        from_attributes = True


class NudgeRequest(BaseModel):
    student_id: int
    nudge_type: str
    context: Optional[Dict[str, Any]] = None


class NudgeResponse(BaseModel):
    student_id: int
    student_name: str
    nudge_type: str
    message: str
    generated_at: datetime


class GroupAnalysisResponse(BaseModel):
    group_id: int
    group_name: str
    health_score: float
    status: str
    issues: List[str]
    recommendations: List[str]
    analyzed_at: datetime


# Dependency for authentication
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    if not config.ENABLE_AUTHENTICATION:
        # In development mode without auth, return a mock admin user
        admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if admin:
            return admin
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No admin user found. Please run database initialization."
        )

    token = credentials.credentials
    user = auth_service.get_current_user(token, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "llm_available": llm_service.is_healthy(),
        "authentication_enabled": config.ENABLE_AUTHENTICATION,
    }


# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        role = UserRole(user_data.role.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: student, instructor, admin"
        )

    user = auth_service.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        role=role,
        db=db
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )

    return user


@app.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token"""
    user = auth_service.authenticate_user(credentials.username, credentials.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_service.create_access_token(
        user_id=user.id,
        username=user.username,
        role=user.role
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }


@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


# Student endpoints
@app.get("/students", response_model=List[StudentResponse])
async def list_students(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all students"""
    students = db.query(Student).offset(skip).limit(limit).all()
    return students


@app.get("/students/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get student by ID"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.get("/students/{student_id}/contributions", response_model=List[ContributionResponse])
async def get_student_contributions(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all contributions for a student"""
    contributions = db.query(Contribution).filter(
        Contribution.student_id == student_id
    ).order_by(Contribution.timestamp.desc()).all()
    return contributions


@app.post("/students/{student_id}/contributions", response_model=ContributionResponse, status_code=status.HTTP_201_CREATED)
async def create_contribution(
    student_id: int,
    contribution: ContributionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new contribution"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    new_contribution = Contribution(
        student_id=student_id,
        task_type=contribution.task_type,
        action=contribution.action,
        hours=contribution.hours,
        timestamp=datetime.utcnow()
    )

    db.add(new_contribution)

    # Update student metrics
    student.total_hours += contribution.hours
    student.tasks_completed += 1
    student.last_activity = datetime.utcnow()

    db.commit()
    db.refresh(new_contribution)

    return new_contribution


# Group endpoints
@app.get("/groups", response_model=List[GroupResponse])
async def list_groups(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all groups"""
    groups = db.query(Group).offset(skip).limit(limit).all()
    return groups


@app.get("/groups/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get group by ID"""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@app.post("/groups", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new group"""
    new_group = Group(
        group_name=group_data.group_name,
        course_id=group_data.course_id,
        project_name=group_data.project_name,
        deadline=group_data.deadline,
        status=GroupStatus.HEALTHY,
        health_score=1.0
    )

    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    return new_group


# AI Agent endpoints
@app.post("/ai/nudge", response_model=NudgeResponse)
async def generate_nudge(
    request: NudgeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a personalized nudge for a student"""
    student = db.query(Student).filter(Student.id == request.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    user = db.query(User).filter(User.id == student.user_id).first()

    contribution_data = {
        "total_hours": student.total_hours,
        "tasks_completed": student.tasks_completed,
        "last_activity": student.last_activity.isoformat() if student.last_activity else "Never"
    }

    try:
        message = llm_service.generate_nudge(
            student_name=user.full_name or user.username,
            contribution_data=contribution_data,
            nudge_type=request.nudge_type,
            context=request.context
        )

        return {
            "student_id": student.id,
            "student_name": user.full_name or user.username,
            "nudge_type": request.nudge_type,
            "message": message,
            "generated_at": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error generating nudge: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate nudge"
        )


@app.get("/ai/group/{group_id}/analyze", response_model=GroupAnalysisResponse)
async def analyze_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze group health and get AI recommendations"""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Get group members and their contributions
    students = db.query(Student).filter(Student.current_group_id == group_id).all()
    participation_data = {}

    for student in students:
        user = db.query(User).filter(User.id == student.user_id).first()
        participation_data[user.full_name or user.username] = student.total_hours

    # Detect issues (simplified)
    issues = []
    if len(participation_data) > 0:
        max_hours = max(participation_data.values()) if participation_data else 0
        total_hours = sum(participation_data.values())

        if max_hours > 0 and total_hours > 0:
            max_percentage = max_hours / total_hours
            if max_percentage > 0.6:
                issues.append("High participation imbalance detected")

        if any(hours == 0 for hours in participation_data.values()):
            issues.append("Some team members are inactive")

    # Analyze with LLM
    try:
        analysis = llm_service.analyze_group_health(
            group_name=group.group_name,
            participation_data=participation_data,
            issues=issues
        )

        return {
            "group_id": group.id,
            "group_name": group.group_name,
            "health_score": group.health_score,
            "status": group.status.value,
            "issues": issues,
            "recommendations": analysis.get("recommendations", []),
            "analyzed_at": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error analyzing group: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze group"
        )


# Statistics endpoints
@app.get("/stats/overview")
async def get_overview_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overview statistics"""
    total_students = db.query(Student).count()
    total_groups = db.query(Group).count()
    total_contributions = db.query(Contribution).count()
    total_hours = db.query(Contribution).with_entities(
        db.func.sum(Contribution.hours)
    ).scalar() or 0

    return {
        "total_students": total_students,
        "total_groups": total_groups,
        "total_contributions": total_contributions,
        "total_hours": float(total_hours),
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )
