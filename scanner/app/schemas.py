"""Pydantic schemas for scanner results"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SeverityLevel(str, Enum):
    """Finding severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ToolStatus(str, Enum):
    """Tool execution status"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"


class FindingSchema(BaseModel):
    """Schema for a security finding"""
    model_config = ConfigDict(use_enum_values=True)
    
    type: str = Field(..., description="Finding type/rule ID")
    severity: SeverityLevel = Field(..., description="Severity level")
    confidence: int = Field(..., ge=0, le=100, description="Confidence score 0-100")
    file_path: str = Field(..., description="Relative file path")
    line_start: int = Field(..., gt=0, description="Starting line number")
    line_end: int = Field(..., gt=0, description="Ending line number")
    message: str = Field(..., description="Finding description")
    code_snippet: Optional[str] = Field(None, description="Code snippet")
    cwe_id: Optional[str] = Field(None, description="CWE identifier")
    owasp_category: Optional[str] = Field(None, description="OWASP category")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Tool-specific metadata")


class ToolResultSchema(BaseModel):
    """Schema for tool execution result"""
    model_config = ConfigDict(use_enum_values=True)
    
    tool_name: str = Field(..., description="Security tool name")
    status: ToolStatus = Field(..., description="Execution status")
    findings: List[FindingSchema] = Field(default_factory=list, description="List of findings")
    execution_time: float = Field(..., description="Execution time in seconds")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    raw_output: Optional[str] = Field(None, description="Raw tool output")


class ScanResultSchema(BaseModel):
    """Schema for complete scan result"""
    model_config = ConfigDict(use_enum_values=True)
    
    scan_id: str = Field(..., description="Scan UUID")
    project_path: str = Field(..., description="Project directory path")
    status: str = Field(..., description="Scan status")
    started_at: datetime = Field(..., description="Scan start time")
    completed_at: Optional[datetime] = Field(None, description="Scan completion time")
    total_findings: int = Field(default=0, description="Total findings count")
    findings: List[FindingSchema] = Field(default_factory=list, description="All findings")
    tools_executed: List[str] = Field(default_factory=list, description="List of executed tools")
    tool_results: List[ToolResultSchema] = Field(default_factory=list, description="Individual tool results")
    execution_time: float = Field(default=0.0, description="Total execution time")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
