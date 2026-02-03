"""Celery application configuration for backend"""
from celery import Celery
import os

# Get configuration from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Create Celery app
celery_app = Celery(
    "backend",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3500,
    result_expires=3600,
    worker_prefetch_multiplier=1,
    task_default_retry_delay=60,
    task_max_retries=3,
)
