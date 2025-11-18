"""
Comprehensive logging setup for Edge AI Collaborative Learning Platform
Provides structured logging with multiple handlers and formatters
"""

import logging
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Optional
import json
from datetime import datetime

from config import config

# Create logs directory
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "ip_address"):
            log_data["ip_address"] = record.ip_address

        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors"""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']

        # Color the level name
        record.levelname = f"{color}{record.levelname}{reset}"

        return super().format(record)


def setup_logging(
    app_name: str = "edge_ai_learning",
    log_level: Optional[str] = None,
    enable_json: bool = False
) -> logging.Logger:
    """
    Setup comprehensive logging for the application

    Args:
        app_name: Name of the application/logger
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_json: Enable JSON formatting for structured logs

    Returns:
        Configured logger instance
    """
    # Get log level from config or parameter
    level = log_level or config.LOG_LEVEL
    log_level_obj = getattr(logging, level.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger(app_name)
    logger.setLevel(log_level_obj)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level_obj)

    if enable_json or config.APP_ENV == "production":
        console_formatter = JSONFormatter()
    else:
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler for all logs (rotating)
    all_logs_file = LOGS_DIR / f"{app_name}.log"
    file_handler = RotatingFileHandler(
        all_logs_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Error log file (only errors and above)
    error_logs_file = LOGS_DIR / f"{app_name}_errors.log"
    error_handler = RotatingFileHandler(
        error_logs_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    logger.addHandler(error_handler)

    # Audit log file (for security events) - timed rotation
    if config.ENABLE_AUDIT_LOG:
        audit_logs_file = LOGS_DIR / f"{app_name}_audit.log"
        audit_handler = TimedRotatingFileHandler(
            audit_logs_file,
            when='midnight',
            interval=1,
            backupCount=365  # Keep 1 year of audit logs
        )
        audit_handler.setLevel(logging.INFO)
        audit_handler.setFormatter(JSONFormatter())

        # Create separate audit logger
        audit_logger = logging.getLogger(f"{app_name}.audit")
        audit_logger.setLevel(logging.INFO)
        audit_logger.addHandler(audit_handler)

    # Sentry integration for error tracking (production)
    if config.SENTRY_DSN and config.APP_ENV == "production":
        try:
            import sentry_sdk
            sentry_sdk.init(
                dsn=config.SENTRY_DSN,
                environment=config.APP_ENV,
                traces_sample_rate=1.0 if config.ENABLE_PERFORMANCE_TRACKING else 0.0,
            )
            logger.info("Sentry error tracking initialized")
        except ImportError:
            logger.warning("Sentry SDK not installed, error tracking disabled")

    # Log startup message
    logger.info(f"Logging initialized for {app_name}")
    logger.info(f"Log level: {level}")
    logger.info(f"Environment: {config.APP_ENV}")
    logger.info(f"Logs directory: {LOGS_DIR.absolute()}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module"""
    return logging.getLogger(f"edge_ai_learning.{name}")


class AuditLogger:
    """Specialized logger for audit events (FERPA compliance)"""

    def __init__(self):
        self.logger = logging.getLogger("edge_ai_learning.audit")

    def log_access(
        self,
        user_id: int,
        username: str,
        resource_type: str,
        resource_id: int,
        action: str,
        ip_address: Optional[str] = None,
        success: bool = True,
        details: Optional[dict] = None
    ):
        """Log data access for compliance"""
        log_data = {
            "event_type": "data_access",
            "user_id": user_id,
            "username": username,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if ip_address:
            log_data["ip_address"] = ip_address

        if details:
            log_data["details"] = details

        self.logger.info(json.dumps(log_data))

    def log_auth_event(
        self,
        username: str,
        event: str,
        success: bool,
        ip_address: Optional[str] = None,
        reason: Optional[str] = None
    ):
        """Log authentication events"""
        log_data = {
            "event_type": "authentication",
            "username": username,
            "event": event,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if ip_address:
            log_data["ip_address"] = ip_address

        if reason:
            log_data["reason"] = reason

        self.logger.info(json.dumps(log_data))

    def log_data_modification(
        self,
        user_id: int,
        username: str,
        resource_type: str,
        resource_id: int,
        action: str,
        changes: dict,
        ip_address: Optional[str] = None
    ):
        """Log data modifications for audit trail"""
        log_data = {
            "event_type": "data_modification",
            "user_id": user_id,
            "username": username,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action,
            "changes": changes,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if ip_address:
            log_data["ip_address"] = ip_address

        self.logger.info(json.dumps(log_data))


# Initialize default logger
default_logger = setup_logging()

# Initialize audit logger
audit_logger = AuditLogger()


if __name__ == "__main__":
    # Test logging
    test_logger = setup_logging("test_app", "DEBUG")

    test_logger.debug("This is a debug message")
    test_logger.info("This is an info message")
    test_logger.warning("This is a warning message")
    test_logger.error("This is an error message")
    test_logger.critical("This is a critical message")

    # Test audit logging
    audit_logger.log_access(
        user_id=1,
        username="test_user",
        resource_type="student",
        resource_id=123,
        action="read",
        ip_address="127.0.0.1",
        success=True
    )

    audit_logger.log_auth_event(
        username="test_user",
        event="login",
        success=True,
        ip_address="127.0.0.1"
    )

    print("\nLog files created in:", LOGS_DIR.absolute())
