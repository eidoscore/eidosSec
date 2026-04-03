"""Add projects.owner_id and scans.task_id columns

Revision ID: 005_add_owner_task_columns
Revises: 004_create_users
Create Date: 2026-04-03 18:40:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '005_add_owner_task_columns'
down_revision = '004_create_users'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('projects', sa.Column('owner_id', UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_projects_owner_id_users',
        'projects',
        'users',
        ['owner_id'],
        ['id'],
        ondelete='SET NULL',
    )
    op.create_index('ix_projects_owner_id', 'projects', ['owner_id'], unique=False)

    op.add_column('scans', sa.Column('task_id', sa.String(length=100), nullable=True))
    op.create_index('ix_scans_task_id', 'scans', ['task_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_scans_task_id', table_name='scans')
    op.drop_column('scans', 'task_id')

    op.drop_index('ix_projects_owner_id', table_name='projects')
    op.drop_constraint('fk_projects_owner_id_users', 'projects', type_='foreignkey')
    op.drop_column('projects', 'owner_id')
