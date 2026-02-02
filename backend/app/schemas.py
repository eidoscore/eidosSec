"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


# Health Check Schemas
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    database: str
    redis: str
    timestamp: datetime


# Project Schemas
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    path: str = Field(..., description="Absolute path to project directory")
    languages: Optional[List[str]] = None
    framework: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    path: str
    languages: List[str]
    framework: Optional[str]
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    id: UUID
    name: str
    path: str
    languages: List[str]
    framework: Optional[str]
    created_at: datetime
    scans_count: int
    
    model_config = ConfigDict(from_attributes=True)


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    path: Optional[str] = Field(None, pattern=r'^/.*')
    framework: Optional[str] = Field(None, max_length=100)
    settings: Optional[Dict[str, Any]] = None


# Scan Schemas
class ScanMode(str, Enum):
    QUICK = "quick"
    DEEP = "deep"
    CUSTOM = "custom"


class ScanCreate(BaseModel):
    project_id: UUID
    mode: ScanMode = ScanMode.QUICK


class ScanResponse(BaseModel):
    id: UUID
    project_id: UUID
    mode: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class ScanListResponse(BaseModel):
    id: UUID
    project_id: UUID
    mode: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    score: Optional[float]
    findings_count: int
    
    model_config = ConfigDict(from_attributes=True)


class ScanDetailResponse(BaseModel):
    id: UUID
    project_id: UUID
    mode: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    score: Optional[float]
    summary: Dict[str, Any]
    tools_executed: List[str]
    error_message: Optional[str]
    findings: List['FindingResponse'] # Forward reference
    
    model_config = ConfigDict(from_attributes=True)


# Finding Schemas
class FindingBase(BaseModel):
    type: str
    severity: str
    confidence: int
    file_path: str
    line_start: int
    line_end: int
    message: str
    code_snippet: Optional[str] = None
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class FindingResponse(FindingBase):
    id: UUID
    scan_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class FindingUpdate(BaseModel):
    """Schema for updating a finding"""
    status: Optional[str] = Field(None, pattern="^(open|fixed|false_positive|accepted_risk|wont_fix)$")
    assigned_to: Optional[str] = Field(None, max_length=100)
    metadata: Optional[Dict[str, Any]] = None


# Pagination
class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    total: int
    page: int
    page_size: int
    items: List[Any]
