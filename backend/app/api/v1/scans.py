"""API endpoints for scanning operations"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, case
from typing import List, Optional
import uuid
from datetime import datetime

from app.database import get_db
from app.models import Project, Scan, Finding, User
from app.services.auth import auth_service
from app.schemas import (
    ScanCreate, 
    ScanResponse, 
    ScanListResponse,
    ScanDetailResponse,
    FindingResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/scans", tags=["scans"])

# Import Celery app from local config
from app.celery_app import celery_app
SCANNER_AVAILABLE = True


@router.post("/", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    scan_data: ScanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Create a new security scan
    
    Creates a scan record and triggers async scan execution via Celery.
    """
    # Verify project exists
    result = await db.execute(
        select(Project).where(Project.id == scan_data.project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {scan_data.project_id} not found"
        )
    
    # Check project ownership (RBAC check)
    if current_user.role != "admin" and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project"
        )
    
    # Tier Gating: Solo users are limited to 3 projects and 1 concurrent scan
    if current_user.role == "user":
        # Check active scans
        active_scans_result = await db.execute(
            select(func.count(Scan.id)).where(
                Scan.status.in_(["pending", "running"]),
                Scan.project_id.in_(
                    select(Project.id).where(Project.owner_id == current_user.id)
                )
            )
        )
        active_count = active_scans_result.scalar_one()
        if active_count >= 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo tier is limited to 1 concurrent scan. Upgrade to PRO for unlimited parallel scans."
            )
    
    # Create scan record
    scan = Scan(
        id=uuid.uuid4(),
        project_id=scan_data.project_id,
        mode=scan_data.mode.value if hasattr(scan_data.mode, "value") else str(scan_data.mode),
        status="pending"
    )
    
    db.add(scan)
    await db.commit()
    await db.refresh(scan)
    
    # Trigger scan task
    if SCANNER_AVAILABLE and celery_app:
        try:
            scan_mode = scan.mode.value if hasattr(scan.mode, "value") else str(scan.mode)
            task = celery_app.send_task(
                "scanner.scan_project",
                args=[project.path, str(scan.id), scan_mode],
                queue="scans"
            )
            # Store task ID for tracking
            scan.task_id = task.id
            scan.status = "running"
            await db.commit()
        except Exception as e:
            # Update scan status to failed
            scan.status = "failed"
            scan.error_message = f"Failed to trigger scan: {str(e)}"
            scan.completed_at = datetime.utcnow()
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to start scan"
            )
    else:
        # Scanner not available
        scan.status = "failed"
        scan.error_message = "Scanner service not available"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Scanner service not available"
        )
    
    return ScanResponse(
        id=scan.id,
        project_id=scan.project_id,
        mode=scan.mode,
        status=scan.status,
        started_at=scan.started_at,
        completed_at=scan.completed_at
    )


@router.get("/stats")
async def get_scan_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Get global scan statistics
    """
    # Total scans
    total_result = await db.execute(select(func.count(Scan.id)))
    total_scans = total_result.scalar_one()
    
    # Active scans (pending or running)
    active_result = await db.execute(
        select(func.count(Scan.id)).where(Scan.status.in_(["pending", "running"]))
    )
    active_scans = active_result.scalar_one()
    
    # Completed today
    today = datetime.now().date()
    today_result = await db.execute(
        select(func.count(Scan.id)).where(func.cast(Scan.completed_at, func.Date) == today)
    )
    completed_today = today_result.scalar_one()
    
    return {
        "total_scans": total_scans,
        "active_scans": active_scans,
        "completed_today": completed_today
    }


@router.get("/", response_model=List[ScanListResponse])
async def list_scans(
    project_id: Optional[uuid.UUID] = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    List scans with optional project filter
    """
    query = select(Scan).order_by(Scan.started_at.desc())
    
    if project_id:
        query = query.where(Scan.project_id == project_id)
    
    # RBAC check
    if current_user.role != "admin":
        query = query.join(Project).where(Project.owner_id == current_user.id)
        
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    scans = result.scalars().all()
    
    return [
        ScanListResponse(
            id=scan.id,
            project_id=scan.project_id,
            mode=scan.mode,
            status=scan.status,
            started_at=scan.started_at,
            completed_at=scan.completed_at,
            score=scan.score,
            findings_count=len(scan.findings) if hasattr(scan, 'findings') else 0
        )
        for scan in scans
    ]


@router.get("/{scan_id}", response_model=ScanDetailResponse)
async def get_scan(
    scan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Get detailed scan information including findings
    """
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id)
    )
    scan = result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan {scan_id} not found"
        )
    
    # RBAC check
    if current_user.role != "admin":
        project_result = await db.execute(
            select(Project).where(Project.id == scan.project_id)
        )
        project = project_result.scalar_one_or_none()
        if not project or project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this scan"
            )
    
    return ScanDetailResponse(
        id=scan.id,
        project_id=scan.project_id,
        mode=scan.mode,
        status=scan.status,
        started_at=scan.started_at,
        completed_at=scan.completed_at,
        duration_seconds=scan.duration_seconds,
        score=scan.score,
        summary=scan.summary,
        tools_executed=scan.tools_executed,
        error_message=scan.error_message,
        findings=scan.findings if hasattr(scan, 'findings') else []
    )


@router.get("/{scan_id}/findings", response_model=PaginatedResponse)
async def list_scan_findings(
    scan_id: uuid.UUID,
    page: int = 1,
    page_size: int = 50,
    severity: Optional[str] = None,
    tool: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Get paginated findings for a specific scan
    """
    # Verify scan exists and check access
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan {scan_id} not found"
        )
    
    # RBAC check
    if current_user.role != "admin":
        project_result = await db.execute(
            select(Project).where(Project.id == scan.project_id)
        )
        project = project_result.scalar_one_or_none()
        if not project or project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to these findings"
            )

    # Build query
    query = select(Finding).where(Finding.scan_id == scan_id)
    
    if severity:
        query = query.where(Finding.severity == severity)
    
    # Filter by tool (checking if tool exists in detected_by_tools JSON array)
    if tool:
        query = query.where(Finding.detected_by_tools.contains([tool]))
    
    # Sort: Critical -> Info, then High Confidence -> Low
    severity_order = case(
        {
            "critical": 1,
            "high": 2,
            "medium": 3,
            "low": 4,
            "info": 5,
        },
        value=Finding.severity,
        else_=6
    )
    
    query = query.order_by(severity_order, desc(Finding.confidence))

    # Calculate total for pagination
    # This is expensive, but simplest for now
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    # Apply pagination
    query = query.limit(page_size).offset((page - 1) * page_size)
    
    result = await db.execute(query)
    findings = result.scalars().all()
    
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=findings
    )


@router.post("/{scan_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_scan(
    scan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Cancel a running scan (revoke Celery task)
    """
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id)
    )
    scan = result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan {scan_id} not found"
        )
    
    # RBAC check
    if current_user.role != "admin":
        project_result = await db.execute(
            select(Project).where(Project.id == scan.project_id)
        )
        project = project_result.scalar_one_or_none()
        if not project or project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this scan"
            )

    if scan.status not in ["pending", "running"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel scan in status {scan.status}"
        )

    if not scan.task_id:
        # If no task_id, just update status
        scan.status = "cancelled"
        scan.error_message = "Scan cancelled by user (no task ID found)"
        scan.completed_at = datetime.utcnow()
        await db.commit()
        return {"message": "Scan status updated to cancelled (no task to revoke)"}

    # Revoke task
    try:
        celery_app.control.revoke(scan.task_id, terminate=True, signal='SIGKILL')
        
        # Update scan record
        scan.status = "cancelled"
        scan.error_message = "Scan cancelled by user"
        scan.completed_at = datetime.utcnow()
        await db.commit()
        
        return {"message": f"Scan {scan_id} cancelled successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel scan task: {str(e)}"
        )


@router.get("/{scan_id}/export")
async def export_scan_findings(
    scan_id: uuid.UUID,
    format: str = "json",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Export findings for a scan
    """
    # Verify scan exists
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan {scan_id} not found"
        )

    # RBAC check
    if current_user.role != "admin":
        project_result = await db.execute(
            select(Project).where(Project.id == scan.project_id)
        )
        project = project_result.scalar_one_or_none()
        if not project or project.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to export this scan"
            )
    
    # Get all findings
    result = await db.execute(
        select(Finding).where(Finding.scan_id == scan_id)
    )
    findings = result.scalars().all()
    
    # Convert to list of dicts for JSON export
    export_data = {
        "scan_id": str(scan.id),
        "project_id": str(scan.project_id),
        "created_at": scan.started_at.isoformat() if scan.started_at else None,
        "findings": [
            {
                "type": f.type,
                "severity": f.severity,
                "description": f.message,
                "file_path": f.file_path,
                "line": f.line_start,
                "confidence": f.confidence,
                "cwe": f.cwe_id
            }
            for f in findings
        ]
    }
    
    return export_data
