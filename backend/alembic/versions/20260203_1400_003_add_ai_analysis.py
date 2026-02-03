"""Add ai_analysis column to findings

Revision ID: 003_add_ai_analysis
Revises: 002_rename_metadata
Create Date: 2026-02-03 14:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = '003_add_ai_analysis'
down_revision = '002_rename_metadata'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('findings', sa.Column('ai_analysis', JSONB, server_default=sa.text("'{}'::jsonb"), nullable=False))


def downgrade() -> None:
    op.drop_column('findings', 'ai_analysis')
