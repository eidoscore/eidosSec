"""API endpoints for scanning operations"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid
from celery.result import AsyncResult

from app.database import get_db
from app.models import Project, Scan
from app.schemas import (
    ScanCreate, 
    ScanResponse, 
    ScanListResponse,
    ScanDetailResponse
)

router = APIRouter(prefix="/scans", tags=["scans"])

# Import Celery app from scanner
try:
    from scanner.app.celery_app import celery_app
    SCANNER_AVAILABLE = True
except ImportError:
    SCANNER_AVAILABLE = False
    celery_app = None


@router.post("/", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    scan_data: ScanCreate,
    db: AsyncSession = Depends(get_db)
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
    
    # Create scan record
    scan = Scan(
        id=uuid.uuid4(),
        project_id=scan_data.project_id,
        mode=scan_data.mode,
        status="pending"
    )
    
    db.add(scan)
    await db.commit()
    await db.refresh(scan)
    
    # Trigger scan task
    if SCANNER_AVAILABLE and celery_app:
        try:
            task = celery_app.send_task(
                "scanner.scan_project",
                args=[project.path, str(scan.id)]
            )
            # Store task ID for tracking
            # TODO: Add task_id field to Scan model
        except Exception as e:
            # Update scan status to failed
            scan.status = "failed"
            scan.error_message = f"Failed to trigger scan: {str(e)}"
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


@router.get("/", response_model=List[ScanListResponse])
async def list_scans(
    project_id: uuid.UUID | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    List scans with optional project filter
    """
    query = select(Scan).order_by(Scan.started_at.desc())
    
    if project_id:
        query = query.where(Scan.project_id == project_id)
    
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
    db: AsyncSession = Depends(get_db)
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
