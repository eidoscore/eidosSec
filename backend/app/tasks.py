"""Celery tasks for backend."""
import asyncio
from datetime import datetime, timezone
import logging
from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy import delete, select

from app.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models import Finding, Scan

logger = logging.getLogger(__name__)


def _parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value

    if isinstance(value, str) and value:
        normalized = value.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(normalized)
        except ValueError:
            return None

    return None


def _normalize_status(raw_status: Any) -> str:
    status = str(raw_status or "failed").lower()
    if status not in {"pending", "running", "completed", "failed", "cancelled"}:
        return "failed"
    return status


def _severity_counts(findings: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for finding in findings:
        severity = str(finding.get("severity", "info")).lower()
        if severity not in counts:
            severity = "info"
        counts[severity] += 1
    return counts


def _calculate_score(counts: Dict[str, int]) -> float:
    # Penalize by severity with heavier weight on critical/high.
    penalty = (
        counts["critical"] * 2.5
        + counts["high"] * 1.5
        + counts["medium"] * 0.75
        + counts["low"] * 0.25
        + counts["info"] * 0.1
    )
    return round(max(0.0, 10.0 - penalty), 1)


async def _process_scan_results_async(scan_id: str, results: Dict[str, Any]) -> Dict[str, Any]:
    scan_uuid = UUID(scan_id)
    incoming_status = _normalize_status(results.get("status"))

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Scan).where(Scan.id == scan_uuid))
        scan = result.scalar_one_or_none()

        if not scan:
            logger.error("Scan %s not found while processing results", scan_id)
            return {"status": "error", "detail": "scan not found"}

        # Do not overwrite terminal cancelled state with late worker updates.
        if scan.status == "cancelled" and incoming_status in {"completed", "failed"}:
            logger.info("Ignoring late %s update for cancelled scan %s", incoming_status, scan_id)
            return {"status": "ignored", "scan_id": scan_id, "reason": "already cancelled"}

        if incoming_status == "running":
            if scan.status == "pending":
                scan.status = "running"
                await db.commit()
            return {"status": "running", "scan_id": scan_id}

        if incoming_status == "cancelled":
            scan.status = "cancelled"
            scan.error_message = str(results.get("error_message") or "Scan cancelled")
            scan.completed_at = _parse_datetime(results.get("completed_at")) or datetime.now(timezone.utc)
            await db.commit()
            return {"status": "cancelled", "scan_id": scan_id}

        if incoming_status == "failed":
            scan.status = "failed"
            scan.error_message = str(
                results.get("error_message")
                or (results.get("metadata") or {}).get("error")
                or "Scan execution failed"
            )
            scan.completed_at = _parse_datetime(results.get("completed_at")) or datetime.now(timezone.utc)

            execution_time = float(results.get("execution_time") or 0)
            scan.duration_seconds = int(round(execution_time)) if execution_time > 0 else scan.duration_seconds
            tools_executed = results.get("tools_executed")
            if isinstance(tools_executed, list):
                scan.tools_executed = tools_executed

            await db.commit()
            return {"status": "failed", "scan_id": scan_id}

        findings_payload = results.get("findings") or []
        findings_data = [f for f in findings_payload if isinstance(f, dict)]

        await db.execute(delete(Finding).where(Finding.scan_id == scan.id))

        for finding_data in findings_data:
            metadata = finding_data.get("metadata")
            metadata = metadata if isinstance(metadata, dict) else {}

            detected_by_tools: List[str] = []
            tool_name = metadata.get("tool")
            if tool_name:
                detected_by_tools.append(str(tool_name))

            line_start = max(1, int(finding_data.get("line_start") or 1))
            line_end = max(line_start, int(finding_data.get("line_end") or line_start))

            finding = Finding(
                scan_id=scan.id,
                type=str(finding_data.get("type") or "unknown"),
                severity=str(finding_data.get("severity") or "info").lower(),
                confidence=max(0, min(100, int(finding_data.get("confidence") or 0))),
                file_path=str(finding_data.get("file_path") or "unknown"),
                line_start=line_start,
                line_end=line_end,
                code_snippet=finding_data.get("code_snippet"),
                message=str(finding_data.get("message") or "No description"),
                cwe_id=finding_data.get("cwe_id"),
                owasp_category=finding_data.get("owasp_category"),
                detected_by_tools=detected_by_tools,
                raw_outputs={},
                metadata=metadata,
                ai_analysis={},
            )
            db.add(finding)

        severity_summary = _severity_counts(findings_data)
        summary = {
            "total_findings": len(findings_data),
            "by_severity": severity_summary,
            "metadata": results.get("metadata") if isinstance(results.get("metadata"), dict) else {},
        }

        execution_time = float(results.get("execution_time") or 0)
        scan.status = "completed"
        scan.completed_at = _parse_datetime(results.get("completed_at")) or datetime.now(timezone.utc)
        scan.duration_seconds = int(round(execution_time)) if execution_time > 0 else scan.duration_seconds
        scan.tools_executed = results.get("tools_executed") if isinstance(results.get("tools_executed"), list) else []
        scan.summary = summary
        scan.score = _calculate_score(severity_summary)
        scan.error_message = None

        await db.commit()
        return {
            "status": "completed",
            "scan_id": scan_id,
            "total_findings": len(findings_data),
            "tools_executed": len(scan.tools_executed),
        }


@celery_app.task(bind=True, max_retries=3, name="app.tasks.process_scan_results")
def process_scan_results(self, scan_id: str, results: dict):
    """Persist scan status/results from scanner worker into backend database."""
    try:
        logger.info("Processing scan results for scan %s", scan_id)
        return asyncio.run(_process_scan_results_async(scan_id, results or {}))
    except Exception as exc:
        logger.error("Failed to process scan results: %s", exc)
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def generate_report(self, project_id: str, report_type: str = "pdf"):
    """Generate security report for a project."""
    try:
        logger.info("Generating %s report for project %s", report_type, project_id)
        # TODO: Implement report generation logic
        return {"status": "success", "project_id": project_id, "type": report_type}
    except Exception as exc:
        logger.error("Failed to generate report: %s", exc)
        raise self.retry(exc=exc, countdown=60)


@celery_app.task
def cleanup_old_scans(days: int = 30):
    """Cleanup scan results older than specified days."""
    logger.info("Cleaning up scans older than %s days", days)
    # TODO: Implement cleanup logic
    return {"status": "success", "cleaned": 0}
