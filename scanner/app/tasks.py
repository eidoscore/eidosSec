"""Celery tasks for scanner operations"""
from pathlib import Path
import logging
from typing import Dict, Any

from app.celery_app import celery_app
from app.orchestrator import ScanOrchestrator
from app.utils import validate_project_path

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="scanner.scan_project")
def scan_project(self, project_path: str, scan_id: str) -> Dict[str, Any]:
    """
    Execute security scan on project
    
    This is the main entry point for scanning. It:
    1. Validates project path exists
    2. Creates orchestrator
    3. Runs scan with all applicable tools
    4. Returns results as dict
    
    Args:
        project_path: Absolute path to project directory
        scan_id: UUID of scan in database
        
    Returns:
        dict containing scan results (findings, tools executed, timing, etc.)
        
    Raises:
        ValueError: If project path is invalid
        Exception: If scan fails unexpectedly
    """
    logger.info(f"Task started: scan_project(project_path={project_path}, scan_id={scan_id})")
    
    try:
        # Validate project path
        project_path_obj = Path(project_path)
        if not validate_project_path(project_path_obj):
            error_msg = f"Invalid project path: {project_path}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Create orchestrator
        orchestrator = ScanOrchestrator(
            project_path=project_path_obj,
            scan_id=scan_id,
            redis_url=celery_app.conf.broker_url
        )
        
        # Run scan
        logger.info(f"Starting scan {scan_id} for {project_path}")
        results = orchestrator.run_scan()
        
        # Convert to dict for Celery serialization
        results_dict = results.dict()
        
        logger.info(
            f"Scan {scan_id} completed successfully: "
            f"{results.total_findings} findings from {len(results.tools_executed)} tools"
        )
        
        return results_dict
        
    except ValueError as e:
        # Invalid input - don't retry
        logger.error(f"Scan {scan_id} failed due to invalid input: {str(e)}")
        raise
        
    except Exception as e:
        # Unexpected error - log and raise for retry
        logger.error(f"Scan {scan_id} failed unexpectedly: {str(e)}", exc_info=True)
        
        # Retry task (Celery will handle this based on config)
        raise self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(name="scanner.health_check")
def health_check() -> Dict[str, str]:
    """
    Health check task to verify scanner worker is operational
    
    Returns:
        dict with status and worker info
    """
    return {
        "status": "healthy",
        "worker": "scanner",
        "tools": ["semgrep", "bandit", "trufflehog", "gitleaks", "trivy"],
        "version": "0.1.0"
    }
