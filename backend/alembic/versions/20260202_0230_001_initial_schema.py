"""Initial schema - projects, scans, findings

Revision ID: 001_initial
Revises: 
Create Date: 2026-02-02 02:30:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('path', sa.Text, nullable=False),
        sa.Column('languages', JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('framework', sa.String(100)),
        sa.Column('settings', JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('idx_projects_name', 'projects', ['name'])
    op.create_index('idx_projects_created_at', 'projects', ['created_at'])
    
    # Create scans table
    op.create_table(
        'scans',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('mode', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('duration_seconds', sa.Integer),
        sa.Column('score', sa.Numeric(3, 1)),
        sa.Column('summary', JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('tools_executed', JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('error_message', sa.Text),
        sa.CheckConstraint("mode IN ('quick', 'deep', 'custom')", name='scans_mode_check'),
        sa.CheckConstraint("status IN ('pending', 'running', 'completed', 'failed', 'cancelled')", name='scans_status_check'),
        sa.CheckConstraint("score >= 0 AND score <= 10", name='scans_score_check'),
        sa.CheckConstraint("completed_at IS NULL OR completed_at >= started_at", name='scans_duration_check'),
    )
    op.create_index('idx_scans_project_id', 'scans', ['project_id'])
    op.create_index('idx_scans_status', 'scans', ['status'])
    op.create_index('idx_scans_started_at', 'scans', ['started_at'])
    
    # Create findings table
    op.create_table(
        'findings',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('scan_id', UUID(as_uuid=True), sa.ForeignKey('scans.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(100), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('confidence', sa.Integer, nullable=False),
        sa.Column('file_path', sa.Text, nullable=False),
        sa.Column('line_start', sa.Integer, nullable=False),
        sa.Column('line_end', sa.Integer, nullable=False),
        sa.Column('code_snippet', sa.Text),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('cwe_id', sa.String(20)),
        sa.Column('owasp_category', sa.String(50)),
        sa.Column('detected_by_tools', JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('raw_outputs', JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('status', sa.String(20), server_default='open'),
        sa.Column('assigned_to', sa.String(100)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("severity IN ('critical', 'high', 'medium', 'low', 'info')", name='findings_severity_check'),
        sa.CheckConstraint("confidence >= 0 AND confidence <= 100", name='findings_confidence_check'),
        sa.CheckConstraint("line_start > 0", name='findings_line_start_check'),
        sa.CheckConstraint("line_end >= line_start", name='findings_line_range_check'),
        sa.CheckConstraint("status IN ('open', 'fixed', 'false_positive', 'accepted_risk', 'wont_fix')", name='findings_status_check'),
    )
    op.create_index('idx_findings_scan_id', 'findings', ['scan_id'])
    op.create_index('idx_findings_severity', 'findings', ['severity'])
    op.create_index('idx_findings_type', 'findings', ['type'])
    op.create_index('idx_findings_status', 'findings', ['status'])
    op.create_index('idx_findings_file_path', 'findings', ['file_path'])
    op.create_index('idx_findings_confidence', 'findings', ['confidence'])


def downgrade() -> None:
    op.drop_table('findings')
    op.drop_table('scans')
    op.drop_table('projects')
