"""Entry point for Celery worker"""
from app.celery_app import celery_app
from app.utils import setup_logging

# Setup logging
setup_logging(level="INFO")

# This file is used by Celery to discover the app
# Usage: celery -A worker worker --loglevel=info
