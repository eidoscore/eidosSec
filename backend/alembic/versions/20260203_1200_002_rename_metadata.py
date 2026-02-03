"""Rename finding_metadata to metadata

Revision ID: 002_rename_metadata
Revises: 001_initial
Create Date: 2026-02-03 12:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_rename_metadata'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename column finding_metadata to metadata in findings table
    op.alter_column('findings', 'finding_metadata', new_column_name='metadata')


def downgrade() -> None:
    # Revert rename
    op.alter_column('findings', 'metadata', new_column_name='finding_metadata')
