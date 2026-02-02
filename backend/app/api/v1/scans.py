"""API endpoints for scanning operations"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import List
import uuid
from celery.result import AsyncResult

from app.database import get_db
from app.models import Project, Scan, Finding
from app.schemas import (
    ScanCreate, 
    ScanResponse, 
    ScanListResponse,
    ScanDetailResponse,
    FindingResponse,
    PaginatedResponse
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


@router.get("/{scan_id}/findings", response_model=PaginatedResponse)
async def list_scan_findings(
    scan_id: uuid.UUID,
    page: int = 1,
    page_size: int = 50,
    severity: str = None,
    tool: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated findings for a specific scan
    """
    # Verify scan exists
    result = await db.execute(
        select(Scan).where(Scan.id == scan_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan {scan_id} not found"
        )

    # Build query
    query = select(Finding).where(Finding.scan_id == scan_id)
    
    if severity:
        query = query.where(Finding.severity == severity)
    
    # Filter by tool (checking if tool exists in detected_by_tools JSON array)
    # This is a simple text check for now, can be improved with JSON operators
    # if tool:
    #    query = query.where(Finding.detected_by_tools.contains([tool]))
    
    # Sort: Critical -> Info, then High Confidence -> Low
    # We map severity to integer for sorting if needed, but for now just text desc
    # 'critical' > 'high' > 'medium' > 'low' > 'info' is NOT alphabetical.
    # We can use a CASE statement or just rely on client side matching for now 
    # OR, since we have a defined set, we could map them. 
    # For simplicity, let's just sort by severity text desc for now, 
    # knowing that c > h > m (alphabetically reversed?)
    # c, h, m, l, i -> c, h, m, l, i
    # alphabetical: critical, high, info, low, medium. That's wrong.
    # Let's just order by confidence for now as primary sort until we add a CASE/ENUM sort.
    query = query.order_by(desc(Finding.confidence))

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


@router.get("/{scan_id}/export")
async def export_scan_findings(
    scan_id: uuid.UUID,
    format: str = "json",
    db: AsyncSession = Depends(get_db)
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
