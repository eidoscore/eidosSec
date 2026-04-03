"""Celery application configuration"""
from celery import Celery
import os

# Get configuration from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://eidossec:password@postgres:5432/eidossec")

# Create Celery app
celery_app = Celery(
    "scanner",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks"]
)

# Configure Celery
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Timezone
    timezone="UTC",
    enable_utc=True,
    
    # Task settings
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes hard limit
    task_soft_time_limit=1700,  # 28 minutes soft limit
    task_acks_late=True,  # Acknowledge after completion
    task_reject_on_worker_lost=True,
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_persistent=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,  # Disable prefetch for long tasks
    worker_max_tasks_per_child=10,  # Restart worker after 10 tasks
    
    # Retry settings
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
)

# Optional: Configure task routes
celery_app.conf.task_routes = {
    "scanner.scan_project": {"queue": "scans"},
    "scanner.health_check": {"queue": "scans"},
    "app.tasks.process_scan_results": {"queue": "backend_tasks"},
}
