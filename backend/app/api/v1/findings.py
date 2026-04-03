"""API endpoints for findings management"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from app.database import get_db
from app.models import Finding, User, Scan, Project
from app.services.auth import auth_service
from app.schemas import FindingResponse, FindingUpdate
from app.services.ai_service import ai_service

router = APIRouter(prefix="/findings", tags=["findings"])


async def _enforce_finding_access(
    db: AsyncSession,
    current_user: User,
    finding: Finding
) -> None:
    """Ensure user can access/mutate finding by project ownership."""
    if current_user.role == "admin":
        return

    scan_result = await db.execute(select(Scan).where(Scan.id == finding.scan_id))
    scan = scan_result.scalar_one_or_none()
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan for this finding no longer exists",
        )

    project_result = await db.execute(select(Project).where(Project.id == scan.project_id))
    project = project_result.scalar_one_or_none()
    if not project or project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this finding",
        )


@router.get("/{finding_id}", response_model=FindingResponse)
async def get_finding(
    finding_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Get finding by ID
    """
    result = await db.execute(
        select(Finding).where(Finding.id == finding_id)
    )
    finding = result.scalar_one_or_none()
    
    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Finding {finding_id} not found"
        )
    
    await _enforce_finding_access(db, current_user, finding)
    
    return finding


@router.patch("/{finding_id}", response_model=FindingResponse)
async def update_finding(
    finding_id: uuid.UUID,
    finding_update: FindingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Update a finding (status, assignee, etc.)
    """
    result = await db.execute(
        select(Finding).where(Finding.id == finding_id)
    )
    finding = result.scalar_one_or_none()
    
    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Finding {finding_id} not found"
        )

    await _enforce_finding_access(db, current_user, finding)
    
    # Update fields
    update_data = finding_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(finding, key, value)
    
    try:
        await db.commit()
        await db.refresh(finding)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update finding: {str(e)}"
        )
        
    return finding


@router.post("/{finding_id}/analyze", response_model=FindingResponse)
async def analyze_finding(
    finding_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    Trigger AI analysis for a specific finding
    """
    result = await db.execute(
        select(Finding).where(Finding.id == finding_id)
    )
    finding = result.scalar_one_or_none()
    
    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Finding {finding_id} not found"
        )

    await _enforce_finding_access(db, current_user, finding)
    
    # Prepare data for AI
    finding_data = {
        "type": finding.type,
        "severity": finding.severity,
        "file_path": finding.file_path,
        "line_start": finding.line_start,
        "message": finding.message,
        "code_snippet": finding.code_snippet
    }
    
    # Perform Analysis
    analysis_result = await ai_service.analyze_finding(finding_data)
    
    # Update Finding
    finding.ai_analysis = analysis_result
    
    try:
        await db.commit()
        await db.refresh(finding)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save AI analysis: {str(e)}"
        )
        
    return finding
