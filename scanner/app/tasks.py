"""Celery tasks for scanner operations"""
from pathlib import Path
import logging
from typing import Dict, Any
from datetime import datetime, timezone
from celery.exceptions import MaxRetriesExceededError

from app.celery_app import celery_app
from app.orchestrator import ScanOrchestrator
from app.utils import validate_project_path

logger = logging.getLogger(__name__)
BACKEND_RESULT_TASK = "app.tasks.process_scan_results"


def _send_result_to_backend(scan_id: str, payload: Dict[str, Any]) -> None:
    """Send scan status/results payload to backend worker for persistence."""
    try:
        celery_app.send_task(
            BACKEND_RESULT_TASK,
            args=[scan_id, payload],
            queue="backend_tasks",
        )
    except Exception as exc:
        logger.error("Failed to send scan update to backend for scan %s: %s", scan_id, exc)


@celery_app.task(bind=True, name="scanner.scan_project")
def scan_project(self, project_path: str, scan_id: str, mode: str = "quick") -> Dict[str, Any]:
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
        mode: Scan profile mode (quick|deep|custom)
        
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
            redis_url=celery_app.conf.broker_url,
            scan_mode=mode,
        )
        
        # Run scan
        logger.info(f"Starting scan {scan_id} for {project_path}")
        _send_result_to_backend(scan_id, {"status": "running"})
        results = orchestrator.run_scan()
        
        # Convert to dict for Celery serialization
        results_dict = results.model_dump(mode="json")
        _send_result_to_backend(scan_id, results_dict)
        
        logger.info(
            f"Scan {scan_id} completed successfully: "
            f"{results.total_findings} findings from {len(results.tools_executed)} tools"
        )
        
        return results_dict
        
    except ValueError as e:
        # Invalid input - don't retry
        logger.error(f"Scan {scan_id} failed due to invalid input: {str(e)}")
        _send_result_to_backend(
            scan_id,
            {
                "status": "failed",
                "error_message": str(e),
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "execution_time": 0,
                "findings": [],
                "tools_executed": [],
                "metadata": {"error": str(e)},
            },
        )
        raise
        
    except Exception as e:
        # Unexpected error - log and raise for retry
        logger.error(f"Scan {scan_id} failed unexpectedly: {str(e)}", exc_info=True)
        
        # Retry task (Celery will handle this based on config)
        try:
            raise self.retry(exc=e, countdown=60, max_retries=3)
        except MaxRetriesExceededError:
            _send_result_to_backend(
                scan_id,
                {
                    "status": "failed",
                    "error_message": str(e),
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "execution_time": 0,
                    "findings": [],
                    "tools_executed": [],
                    "metadata": {"error": str(e)},
                },
            )
            raise


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
