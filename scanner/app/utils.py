"""Utility functions for scanner"""
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO") -> None:
    """Configure logging for scanner application"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def validate_project_path(project_path: Path) -> bool:
    """
    Validate that project path exists and is accessible
    
    Args:
        project_path: Path to project directory
        
    Returns:
        True if valid, False otherwise
    """
    if not project_path.exists():
        logger.error(f"Project path does not exist: {project_path}")
        return False
    
    if not project_path.is_dir():
        logger.error(f"Project path is not a directory: {project_path}")
        return False
    
    # Check if we can read the directory
    try:
        list(project_path.iterdir())
        return True
    except PermissionError:
        logger.error(f"Permission denied for project path: {project_path}")
        return False


def extract_relative_path(file_path: str, project_path: Path) -> str:
    """
    Convert absolute file path to relative path from project root
    
    Args:
        file_path: Absolute or relative file path
        project_path: Project root directory
        
    Returns:
        Relative path from project root
    """
    try:
        abs_file = Path(file_path).resolve()
        abs_project = project_path.resolve()
        return str(abs_file.relative_to(abs_project))
    except ValueError:
        # File is not relative to project, return as-is
        return file_path


def sanitize_finding_message(message: str, max_length: int = 500) -> str:
    """
    Sanitize and truncate finding message
    
    Args:
        message: Original message
        max_length: Maximum message length
        
    Returns:
        Sanitized message
    """
    if not message:
        return "No description provided"
    
    # Remove excessive whitespace
    message = " ".join(message.split())
    
    # Truncate if too long
    if len(message) > max_length:
        message = message[:max_length - 3] + "..."
    
    return message


def calculate_confidence(tool_name: str, severity: str, **kwargs) -> int:
    """
    Calculate confidence score based on tool and finding characteristics
    
    Args:
        tool_name: Name of security tool
        severity: Finding severity
        **kwargs: Additional tool-specific parameters
        
    Returns:
        Confidence score 0-100
    """
    # Base confidence by tool (based on false positive rates)
    base_confidence = {
        "semgrep": 85,
        "bandit": 80,
        "trufflehog": 70,  # Higher false positives for secrets
        "gitleaks": 75,
        "trivy": 90,  # CVE database is highly accurate
    }
    
    confidence = base_confidence.get(tool_name.lower(), 70)
    
    # Adjust based on severity (higher severity = higher confidence in reporting)
    severity_adjustment = {
        "critical": 10,
        "high": 5,
        "medium": 0,
        "low": -5,
        "info": -10
    }
    
    confidence += severity_adjustment.get(severity.lower(), 0)
    
    # Ensure within bounds
    return max(0, min(100, confidence))
