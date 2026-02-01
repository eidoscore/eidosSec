"""API endpoints for project management"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from app.database import get_db
from app.models import Project
from app.schemas import ProjectCreate, ProjectResponse, ProjectListResponse

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new project
    """
    # Check if project with same name exists
    result = await db.execute(
        select(Project).where(Project.name == project_data.name)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project with name '{project_data.name}' already exists"
        )
    
    # Create project
    project = Project(
        id=uuid.uuid4(),
        name=project_data.name,
        path=project_data.path,
        languages=project_data.languages or [],
        framework=project_data.framework,
        settings=project_data.settings or {}
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    return ProjectResponse(
        id=project.id,
        name=project.name,
        path=project.path,
        languages=project.languages,
        framework=project.framework,
        settings=project.settings,
        created_at=project.created_at,
        updated_at=project.updated_at
    )


@router.get("/", response_model=List[ProjectListResponse])
async def list_projects(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    List all projects
    """
    result = await db.execute(
        select(Project).order_by(Project.created_at.desc()).limit(limit).offset(offset)
    )
    projects = result.scalars().all()
    
    return [
        ProjectListResponse(
            id=project.id,
            name=project.name,
            path=project.path,
            languages=project.languages,
            framework=project.framework,
            created_at=project.created_at,
            scans_count=len(project.scans) if hasattr(project, 'scans') else 0
        )
        for project in projects
    ]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get project by ID
    """
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found"
        )
    
    return ProjectResponse(
        id=project.id,
        name=project.name,
        path=project.path,
        languages=project.languages,
        framework=project.framework,
        settings=project.settings,
        created_at=project.created_at,
        updated_at=project.updated_at
    )
