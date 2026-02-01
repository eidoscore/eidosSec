"""SQLAlchemy database models"""
from sqlalchemy import Column, String, Text, Integer, Numeric, ForeignKey, TIMESTAMP, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Project(Base):
    """Project model - represents a codebase to scan"""
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    path = Column(Text, nullable=False)
    languages = Column(JSONB, default=list, nullable=False)
    framework = Column(String(100))
    settings = Column(JSONB, default=dict, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    scans = relationship("Scan", back_populates="project", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("path ~ '^/.*'", name="projects_path_check"),
    )


class Scan(Base):
    """Scan model - represents a security scan run"""
    __tablename__ = "scans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    mode = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, index=True)
    started_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, index=True)
    completed_at = Column(TIMESTAMP(timezone=True))
    duration_seconds = Column(Integer)
    score = Column(Numeric(3, 1))
    summary = Column(JSONB, default=dict, nullable=False)
    tools_executed = Column(JSONB, default=list, nullable=False)
    error_message = Column(Text)
    
    # Relationships
    project = relationship("Project", back_populates="scans")
    findings = relationship("Finding", back_populates="scan", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("mode IN ('quick', 'deep', 'custom')", name="scans_mode_check"),
        CheckConstraint("status IN ('pending', 'running', 'completed', 'failed', 'cancelled')", name="scans_status_check"),
        CheckConstraint("score >= 0 AND score <= 10", name="scans_score_check"),
        CheckConstraint("completed_at IS NULL OR completed_at >= started_at", name="scans_duration_check"),
    )


class Finding(Base):
    """Finding model - represents a security issue discovered"""
    __tablename__ = "findings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(100), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    confidence = Column(Integer, nullable=False, index=True)
    file_path = Column(Text, nullable=False, index=True)
    line_start = Column(Integer, nullable=False)
    line_end = Column(Integer, nullable=False)
    code_snippet = Column(Text)
    message = Column(Text, nullable=False)
    cwe_id = Column(String(20))
    owasp_category = Column(String(50))
    detected_by_tools = Column(JSONB, nullable=False, default=list)
    raw_outputs = Column(JSONB, default=dict, nullable=False)
    status = Column(String(20), default="open", index=True)
    assigned_to = Column(String(100))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    scan = relationship("Scan", back_populates="findings")
    
    __table_args__ = (
        CheckConstraint("severity IN ('critical', 'high', 'medium', 'low', 'info')", name="findings_severity_check"),
        CheckConstraint("confidence >= 0 AND confidence <= 100", name="findings_confidence_check"),
        CheckConstraint("line_start > 0", name="findings_line_start_check"),
        CheckConstraint("line_end >= line_start", name="findings_line_range_check"),
        CheckConstraint("status IN ('open', 'fixed', 'false_positive', 'accepted_risk', 'wont_fix')", name="findings_status_check"),
    )
