"""
Monitoring and observability for Edge AI Collaborative Learning Platform
Provides metrics, health checks, and performance tracking
"""

import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps
from collections import defaultdict
import threading

from config import config

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Simple metrics collector for monitoring application performance"""

    def __init__(self):
        self.metrics = defaultdict(lambda: {"count": 0, "total_time": 0, "errors": 0})
        self.lock = threading.Lock()

    def record_request(
        self,
        endpoint: str,
        duration: float,
        success: bool = True
    ):
        """Record an API request metric"""
        with self.lock:
            self.metrics[endpoint]["count"] += 1
            self.metrics[endpoint]["total_time"] += duration
            if not success:
                self.metrics[endpoint]["errors"] += 1

    def record_llm_call(
        self,
        model: str,
        duration: float,
        tokens: Optional[int] = None,
        success: bool = True
    ):
        """Record an LLM call metric"""
        key = f"llm_{model}"
        with self.lock:
            self.metrics[key]["count"] += 1
            self.metrics[key]["total_time"] += duration
            if tokens:
                self.metrics[key].setdefault("total_tokens", 0)
                self.metrics[key]["total_tokens"] += tokens
            if not success:
                self.metrics[key]["errors"] += 1

    def record_database_query(
        self,
        query_type: str,
        duration: float,
        success: bool = True
    ):
        """Record a database query metric"""
        key = f"db_{query_type}"
        with self.lock:
            self.metrics[key]["count"] += 1
            self.metrics[key]["total_time"] += duration
            if not success:
                self.metrics[key]["errors"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        with self.lock:
            # Calculate averages
            result = {}
            for key, data in self.metrics.items():
                result[key] = {
                    "count": data["count"],
                    "total_time": round(data["total_time"], 3),
                    "avg_time": round(
                        data["total_time"] / data["count"] if data["count"] > 0 else 0,
                        3
                    ),
                    "errors": data["errors"],
                    "error_rate": round(
                        data["errors"] / data["count"] if data["count"] > 0 else 0,
                        3
                    )
                }
                if "total_tokens" in data:
                    result[key]["total_tokens"] = data["total_tokens"]
                    result[key]["avg_tokens"] = round(
                        data["total_tokens"] / data["count"] if data["count"] > 0 else 0,
                        2
                    )
            return result

    def reset_metrics(self):
        """Reset all metrics"""
        with self.lock:
            self.metrics.clear()


# Global metrics collector
metrics_collector = MetricsCollector()


def track_time(metric_name: str):
    """Decorator to track execution time of functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                metrics_collector.record_request(metric_name, duration, success)
                if duration > 1.0:  # Log slow operations
                    logger.warning(
                        f"Slow operation: {metric_name} took {duration:.2f}s"
                    )
        return wrapper
    return decorator


class HealthCheck:
    """Health check system for monitoring service dependencies"""

    @staticmethod
    def check_database() -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            from database import engine
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return {"status": "healthy", "message": "Database connection OK"}
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"status": "unhealthy", "message": str(e)}

    @staticmethod
    def check_llm() -> Dict[str, Any]:
        """Check LLM service availability"""
        try:
            from llm_integration import llm_service
            if llm_service.is_healthy():
                return {"status": "healthy", "message": "LLM service available"}
            else:
                return {"status": "degraded", "message": "LLM service unavailable"}
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            return {"status": "unhealthy", "message": str(e)}

    @staticmethod
    def check_lms() -> Dict[str, Any]:
        """Check LMS integration"""
        try:
            from lms_integration import lms_provider
            if lms_provider and lms_provider.is_available():
                return {"status": "healthy", "message": "LMS integration active"}
            else:
                return {"status": "degraded", "message": "LMS integration not configured"}
        except Exception as e:
            logger.error(f"LMS health check failed: {e}")
            return {"status": "unhealthy", "message": str(e)}

    @staticmethod
    def check_redis() -> Dict[str, Any]:
        """Check Redis connectivity"""
        if not config.ENABLE_REDIS:
            return {"status": "disabled", "message": "Redis not enabled"}

        try:
            import redis
            r = redis.from_url(config.REDIS_URL)
            r.ping()
            return {"status": "healthy", "message": "Redis connection OK"}
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {"status": "unhealthy", "message": str(e)}

    @staticmethod
    def get_overall_health() -> Dict[str, Any]:
        """Get overall system health"""
        checks = {
            "database": HealthCheck.check_database(),
            "llm": HealthCheck.check_llm(),
            "lms": HealthCheck.check_lms(),
            "redis": HealthCheck.check_redis(),
        }

        # Determine overall status
        statuses = [check["status"] for check in checks.values()]
        if all(s == "healthy" or s == "disabled" for s in statuses):
            overall_status = "healthy"
        elif any(s == "unhealthy" for s in statuses):
            overall_status = "unhealthy"
        else:
            overall_status = "degraded"

        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks,
            "metrics": metrics_collector.get_metrics()
        }


class PerformanceMonitor:
    """Monitor performance of critical operations"""

    def __init__(self):
        self.slow_queries = []
        self.error_log = []
        self.max_log_size = 100

    def log_slow_query(
        self,
        query: str,
        duration: float,
        context: Optional[Dict[str, Any]] = None
    ):
        """Log a slow database query"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query[:200],  # Truncate long queries
            "duration": round(duration, 3),
            "context": context or {}
        }

        self.slow_queries.append(entry)
        if len(self.slow_queries) > self.max_log_size:
            self.slow_queries.pop(0)

        logger.warning(f"Slow query ({duration:.2f}s): {query[:100]}")

    def log_error(
        self,
        error_type: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Log an application error"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": error_type,
            "message": message,
            "context": context or {}
        }

        self.error_log.append(entry)
        if len(self.error_log) > self.max_log_size:
            self.error_log.pop(0)

    def get_slow_queries(self) -> list:
        """Get recent slow queries"""
        return self.slow_queries[-20:]  # Return last 20

    def get_recent_errors(self) -> list:
        """Get recent errors"""
        return self.error_log[-20:]  # Return last 20


# Global performance monitor
performance_monitor = PerformanceMonitor()


def get_system_stats() -> Dict[str, Any]:
    """Get system statistics"""
    import psutil

    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    # Test monitoring
    print("Testing monitoring system...")

    # Test metrics
    metrics_collector.record_request("/api/test", 0.5, True)
    metrics_collector.record_request("/api/test", 0.3, True)
    metrics_collector.record_llm_call("gpt-4", 2.5, 150, True)

    print("\nMetrics:")
    import json
    print(json.dumps(metrics_collector.get_metrics(), indent=2))

    # Test health check
    print("\nHealth Check:")
    health = HealthCheck.get_overall_health()
    print(json.dumps(health, indent=2))
