"""
Configuration Management for Edge AI Collaborative Learning Platform
Loads and validates configuration from environment variables
"""

import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Main configuration class"""

    # Application Settings
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./edge_ai_learning.db"
    )

    # LLM Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")

    # Ollama Settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:latest")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "120"))

    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    # Hugging Face Settings
    HUGGINGFACE_API_KEY: Optional[str] = os.getenv("HUGGINGFACE_API_KEY")
    HUGGINGFACE_MODEL: str = os.getenv("HUGGINGFACE_MODEL", "meta-llama/Llama-2-7b-chat-hf")

    # LMS Integration
    LMS_PROVIDER: str = os.getenv("LMS_PROVIDER", "canvas")
    LMS_API_URL: Optional[str] = os.getenv("LMS_API_URL")
    LMS_API_KEY: Optional[str] = os.getenv("LMS_API_KEY")
    LMS_SYNC_INTERVAL: int = int(os.getenv("LMS_SYNC_INTERVAL", "300"))

    # Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    ENABLE_AUTHENTICATION: bool = os.getenv("ENABLE_AUTHENTICATION", "true").lower() == "true"

    # Session Management
    SESSION_COOKIE_NAME: str = os.getenv("SESSION_COOKIE_NAME", "edge_ai_session")
    SESSION_COOKIE_SECURE: bool = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    SESSION_COOKIE_HTTPONLY: bool = os.getenv("SESSION_COOKIE_HTTPONLY", "true").lower() == "true"
    SESSION_COOKIE_SAMESITE: str = os.getenv("SESSION_COOKIE_SAMESITE", "lax")

    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_WORKERS: int = int(os.getenv("API_WORKERS", "4"))
    API_RATE_LIMIT: int = int(os.getenv("API_RATE_LIMIT", "100"))

    # Streamlit Configuration
    STREAMLIT_SERVER_PORT: int = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    STREAMLIT_SERVER_ADDRESS: str = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")
    STREAMLIT_SERVER_HEADLESS: bool = os.getenv("STREAMLIT_SERVER_HEADLESS", "true").lower() == "true"

    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    ENABLE_REDIS: bool = os.getenv("ENABLE_REDIS", "false").lower() == "true"

    # Agent Configuration
    PERSONAL_AGENT_INACTIVITY_DAYS: int = int(os.getenv("PERSONAL_AGENT_INACTIVITY_DAYS", "3"))
    PERSONAL_AGENT_WORKLOAD_THRESHOLD: float = float(os.getenv("PERSONAL_AGENT_WORKLOAD_THRESHOLD", "0.5"))
    GROUP_AGENT_IMBALANCE_THRESHOLD: float = float(os.getenv("GROUP_AGENT_IMBALANCE_THRESHOLD", "0.6"))
    INSTRUCTOR_AGENT_ALERT_THRESHOLD: float = float(os.getenv("INSTRUCTOR_AGENT_ALERT_THRESHOLD", "0.5"))

    # Privacy and Compliance
    ENABLE_ENCRYPTION: bool = os.getenv("ENABLE_ENCRYPTION", "true").lower() == "true"
    FERPA_COMPLIANT_MODE: bool = os.getenv("FERPA_COMPLIANT_MODE", "true").lower() == "true"
    DATA_RETENTION_DAYS: int = int(os.getenv("DATA_RETENTION_DAYS", "365"))
    ENABLE_AUDIT_LOG: bool = os.getenv("ENABLE_AUDIT_LOG", "true").lower() == "true"

    # Monitoring and Observability
    ENABLE_MONITORING: bool = os.getenv("ENABLE_MONITORING", "true").lower() == "true"
    METRICS_PORT: int = int(os.getenv("METRICS_PORT", "9090"))
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    ENABLE_PERFORMANCE_TRACKING: bool = os.getenv("ENABLE_PERFORMANCE_TRACKING", "true").lower() == "true"

    # Email Notifications
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    ENABLE_EMAIL_NOTIFICATIONS: bool = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "false").lower() == "true"

    # Development Settings
    MOCK_LLM_RESPONSES: bool = os.getenv("MOCK_LLM_RESPONSES", "false").lower() == "true"
    ENABLE_SWAGGER_UI: bool = os.getenv("ENABLE_SWAGGER_UI", "true").lower() == "true"
    ENABLE_CORS: bool = os.getenv("ENABLE_CORS", "true").lower() == "true"
    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:8501"
    ).split(",")

    @classmethod
    def validate(cls) -> bool:
        """Validate critical configuration settings"""
        errors = []

        # Check SECRET_KEY in production
        if cls.APP_ENV == "production" and cls.SECRET_KEY == "dev-secret-key-change-in-production":
            errors.append("SECRET_KEY must be changed in production")

        # Check JWT_SECRET_KEY in production
        if cls.APP_ENV == "production" and cls.JWT_SECRET_KEY == "jwt-secret-key-change-in-production":
            errors.append("JWT_SECRET_KEY must be changed in production")

        # Check LLM provider configuration
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required when LLM_PROVIDER is 'openai'")

        if cls.LLM_PROVIDER == "huggingface" and not cls.HUGGINGFACE_API_KEY:
            errors.append("HUGGINGFACE_API_KEY is required when LLM_PROVIDER is 'huggingface'")

        # Check LMS configuration if needed
        if cls.LMS_API_URL and not cls.LMS_API_KEY:
            errors.append("LMS_API_KEY is required when LMS_API_URL is configured")

        # Check email configuration if enabled
        if cls.ENABLE_EMAIL_NOTIFICATIONS and (not cls.SMTP_USER or not cls.SMTP_PASSWORD):
            errors.append("SMTP_USER and SMTP_PASSWORD are required when email notifications are enabled")

        if errors:
            error_msg = "\n".join([f"  - {err}" for err in errors])
            raise ValueError(f"Configuration validation failed:\n{error_msg}")

        return True

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode"""
        return cls.APP_ENV == "production"

    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development mode"""
        return cls.APP_ENV == "development"

    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL with proper formatting"""
        return cls.DATABASE_URL

    @classmethod
    def get_llm_config(cls) -> dict:
        """Get LLM configuration based on provider"""
        if cls.LLM_PROVIDER == "ollama":
            return {
                "provider": "ollama",
                "base_url": cls.OLLAMA_BASE_URL,
                "model": cls.OLLAMA_MODEL,
                "timeout": cls.OLLAMA_TIMEOUT,
            }
        elif cls.LLM_PROVIDER == "openai":
            return {
                "provider": "openai",
                "api_key": cls.OPENAI_API_KEY,
                "model": cls.OPENAI_MODEL,
                "base_url": cls.OPENAI_BASE_URL,
            }
        elif cls.LLM_PROVIDER == "huggingface":
            return {
                "provider": "huggingface",
                "api_key": cls.HUGGINGFACE_API_KEY,
                "model": cls.HUGGINGFACE_MODEL,
            }
        else:
            raise ValueError(f"Unsupported LLM provider: {cls.LLM_PROVIDER}")


# Singleton instance
config = Config()

# Validate configuration on import (can be disabled for testing)
if os.getenv("SKIP_CONFIG_VALIDATION", "false").lower() != "true":
    try:
        config.validate()
    except ValueError as e:
        if config.APP_ENV == "production":
            raise
        else:
            print(f"Warning: {e}")
            print("Continuing in development mode with default values")
