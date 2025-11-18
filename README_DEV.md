# Edge AI Collaborative Learning Platform - Production Version

This is the production-ready version of the Edge AI Collaborative Learning Platform, evolved from the initial PoC.

## 🚀 What's New in the Production Version

### Core Infrastructure

✅ **Production-Ready Architecture**
- FastAPI REST API with full CRUD operations
- SQLAlchemy ORM with PostgreSQL/SQLite support
- Comprehensive authentication and authorization (JWT-based)
- Role-based access control (Student, Instructor, Admin)

✅ **Real LLM Integration**
- Support for multiple LLM providers:
  - Ollama (local deployment)
  - OpenAI API
  - Hugging Face
- Fallback to mock responses when LLM unavailable
- Configurable model selection

✅ **Database Persistence**
- Full relational database schema
- User management and profiles
- Course and group management
- Contribution tracking
- Communication logs
- Audit trails for FERPA compliance

✅ **Security & Compliance**
- JWT-based authentication
- Password hashing with bcrypt
- FERPA-compliant audit logging
- Data encryption options
- Role-based permissions

### Features Added

✅ **LMS Integration Framework**
- Canvas LMS support
- Moodle LMS support
- Automatic data synchronization
- Course, student, and group sync

✅ **Monitoring & Observability**
- Comprehensive logging system
- Performance metrics collection
- Health check endpoints
- Error tracking and reporting
- Slow query detection

✅ **Testing Infrastructure**
- Pytest-based test suite
- Unit tests for core components
- API integration tests
- Test coverage reporting

✅ **Docker Deployment**
- Multi-container Docker Compose setup
- PostgreSQL database container
- Redis caching container
- Ollama LLM container
- Automatic health checks

### Developer Experience

✅ **Configuration Management**
- Environment-based configuration
- Centralized config module
- Validation and defaults
- `.env.example` template

✅ **Documentation**
- Comprehensive deployment guide
- API documentation (OpenAPI/Swagger)
- Code documentation and comments
- Architecture diagrams

## 📋 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone <repo-url>
cd edge-ai-collaborative-learning-poc
git checkout dev

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start all services
docker-compose up -d

# Initialize database
docker-compose exec api python scripts/init_db.py

# Pull LLM model (if using Ollama)
docker-compose exec ollama ollama pull qwen2.5-coder:latest

# Access the application
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# UI: http://localhost:8501
```

### Option 2: Manual Setup

```bash
# Install dependencies
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env

# Initialize database
python database.py
python scripts/init_db.py

# Start API
uvicorn api:app --reload --port 8000

# In another terminal, start UI
streamlit run app.py
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                 Streamlit UI                    │
│              (User Interface)                   │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│              FastAPI REST API                   │
│         (Business Logic Layer)                  │
└─────┬──────────┬──────────┬────────────────────┘
      │          │          │
┌─────▼───┐ ┌────▼────┐ ┌──▼──────────────┐
│Database │ │   LLM   │ │  LMS Integration│
│(Postgres│ │(Ollama/ │ │  (Canvas/Moodle)│
│/SQLite) │ │OpenAI)  │ └─────────────────┘
└─────────┘ └─────────┘
```

## 📁 Project Structure

```
edge-ai-collaborative-learning-poc/
├── api.py                    # FastAPI application
├── app.py                    # Streamlit UI (updated)
├── agentic_system.py         # AI agent logic (updated)
├── config.py                 # Configuration management
├── database.py               # Database models and setup
├── auth.py                   # Authentication & authorization
├── llm_integration.py        # LLM provider abstraction
├── lms_integration.py        # LMS integration framework
├── logger.py                 # Logging configuration
├── monitoring.py             # Metrics and health checks
├── sample_data.py            # Sample data generator
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
├── Dockerfile                # Docker container definition
├── docker-compose.yml        # Multi-container orchestration
├── pytest.ini                # Test configuration
├── DEPLOYMENT.md             # Deployment guide
├── scripts/
│   └── init_db.py           # Database initialization
├── tests/
│   ├── test_auth.py         # Authentication tests
│   └── test_api.py          # API tests
└── documentation/           # Original PoC documentation
```

## 🔑 Key Components

### 1. REST API (`api.py`)

Full-featured REST API with:
- Authentication endpoints (`/auth/register`, `/auth/login`)
- Student management (`/students/*`)
- Group management (`/groups/*`)
- Contribution tracking (`/students/{id}/contributions`)
- AI agent endpoints (`/ai/nudge`, `/ai/group/{id}/analyze`)
- Statistics and metrics (`/stats/overview`)

**API Documentation**: Available at `/docs` when running

### 2. Database Layer (`database.py`)

Complete relational schema:
- Users (with role-based access)
- Students and Instructors
- Courses and Groups
- Contributions and Milestones
- Communications
- Audit logs

### 3. LLM Integration (`llm_integration.py`)

Multi-provider support:
```python
from llm_integration import llm_service

# Generate a nudge
nudge = llm_service.generate_nudge(
    student_name="Alice",
    contribution_data={"total_hours": 5, ...},
    nudge_type="positive"
)
```

### 4. Authentication (`auth.py`)

JWT-based authentication:
```python
from auth import auth_service

# Create user
user = auth_service.create_user(
    username="student1",
    email="student@edu",
    password="secure123",
    role=UserRole.STUDENT
)

# Authenticate
token = auth_service.create_access_token(user.id, user.username, user.role)
```

### 5. LMS Integration (`lms_integration.py`)

Sync data from LMS:
```python
from lms_integration import lms_sync_service

# Sync courses
lms_sync_service.sync_courses(db)

# Sync students
lms_sync_service.sync_students(db, course_id)
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run tests by marker
pytest -m unit
pytest -m integration
```

## 📊 Monitoring

### Health Checks

```bash
# Check overall health
curl http://localhost:8000/health

# Response:
{
  "status": "healthy",
  "timestamp": "2024-...",
  "llm_available": true,
  "authentication_enabled": true
}
```

### Metrics

```python
from monitoring import metrics_collector

# View metrics
metrics = metrics_collector.get_metrics()
```

### Logs

Logs are written to:
- `logs/edge_ai_learning.log` - All logs
- `logs/edge_ai_learning_errors.log` - Errors only
- `logs/edge_ai_learning_audit.log` - Audit trail (FERPA)

## 🔒 Security

### Production Checklist

- [ ] Change all default passwords
- [ ] Generate strong secret keys (32+ characters)
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall rules
- [ ] Set `APP_ENV=production`
- [ ] Enable audit logging
- [ ] Configure database backups
- [ ] Review FERPA compliance settings
- [ ] Set up monitoring and alerts

### Environment Variables

Critical security settings:
```bash
SECRET_KEY=<generate-random-32-char-key>
JWT_SECRET_KEY=<generate-random-32-char-key>
ENABLE_ENCRYPTION=true
FERPA_COMPLIANT_MODE=true
ENABLE_AUDIT_LOG=true
```

## 🚢 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive deployment instructions including:

- Docker deployment
- Manual deployment
- Nginx reverse proxy setup
- SSL/TLS configuration
- Database backups
- Monitoring setup
- Troubleshooting guide

## 🔄 Migration from PoC

The original PoC functionality is preserved and enhanced:

| PoC Feature | Production Status |
|-------------|-------------------|
| Template-based nudges | ✅ Enhanced with real LLM |
| In-memory data | ✅ Migrated to database |
| Single Streamlit app | ✅ + REST API added |
| Sample data only | ✅ + LMS integration |
| No authentication | ✅ Full auth system |
| No persistence | ✅ PostgreSQL/SQLite |
| Local only | ✅ Docker deployment |

## 📚 API Examples

### Register a User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@edu",
    "password": "secure123",
    "full_name": "Alice Wonderland",
    "role": "student"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "secure123"
  }'
```

### Generate a Nudge

```bash
curl -X POST "http://localhost:8000/ai/nudge" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "nudge_type": "positive",
    "context": {"recent_contribution": "Completed milestone"}
  }'
```

## 🤝 Contributing

This is the production development branch. For contributing:

1. Create a feature branch from `dev`
2. Make your changes
3. Add tests
4. Submit a pull request

## 📄 License

See LICENSE file for details.

## 🆘 Support

- **Documentation**: See `documentation/` folder
- **Deployment Issues**: Check `DEPLOYMENT.md`
- **API Questions**: View `/docs` endpoint
- **Original PoC**: See `README.md` in root

## 🎯 Roadmap

Future enhancements:
- [ ] Advanced analytics dashboard
- [ ] Mobile app support
- [ ] Real-time collaboration features
- [ ] Advanced ML models for predictions
- [ ] Multi-institution support
- [ ] Integration with more LMS platforms
- [ ] Enhanced privacy controls
- [ ] GraphQL API option

---

**Version**: 1.0.0 (Production)
**Based on**: Edge AI Collaborative Learning PoC
**Status**: Production-ready
