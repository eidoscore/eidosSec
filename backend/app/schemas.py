"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


# Health Check Schemas
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    database: str
    redis: str
    timestamp: datetime


# Project Schemas
class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=1, max_length=255)
    path: str = Field(..., pattern=r'^/.*')
    framework: Optional[str] = Field(None, max_length=100)


class ProjectCreate(ProjectBase):
    """Schema for creating a project"""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    path: Optional[str] = Field(None, pattern=r'^/.*')
    framework: Optional[str] = Field(None, max_length=100)
    settings: Optional[Dict[str, Any]] = None


class ProjectResponse(ProjectBase):
    """Schema for project response"""
    id: UUID
    languages: List[str]
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Scan Schemas
class ScanCreate(BaseModel):
    """Schema for creating a scan"""
    project_id: UUID
    mode: str = Field(..., pattern=r'^(quick|deep|custom)$')


class ScanResponse(BaseModel):
    """Schema for scan response"""
    id: UUID
    project_id: UUID
    mode: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    score: Optional[float] = None
    summary: Dict[str, Any]
    tools_executed: List[str]
    error_message: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# Finding Schemas
class FindingResponse(BaseModel):
    """Schema for finding response"""
    id: UUID
    scan_id: UUID
    type: str
    severity: str
    confidence: int
    file_path: str
    line_start: int
    line_end: int
    code_snippet: Optional[str] = None
    message: str
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None
    detected_by_tools: List[str]
    raw_outputs: Dict[str, Any]
    status: str
    assigned_to: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Pagination
class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    total: int
    page: int
    page_size: int
    items: List[Any]
