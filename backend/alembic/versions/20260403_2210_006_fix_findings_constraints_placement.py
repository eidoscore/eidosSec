"""Fix findings constraint placement and clean up stray user constraints

Revision ID: 006_fix_findings_constraints_placement
Revises: 005_add_owner_task_columns
Create Date: 2026-04-03 22:10:00
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "006_fix_findings_constraints_placement"
down_revision = "005_add_owner_task_columns"
branch_labels = None
depends_on = None


FINDINGS_CHECK_CONSTRAINTS = {
    "findings_severity_check": "severity IN ('critical', 'high', 'medium', 'low', 'info')",
    "findings_confidence_check": "confidence >= 0 AND confidence <= 100",
    "findings_line_start_check": "line_start > 0",
    "findings_line_range_check": "line_end >= line_start",
    "findings_status_check": "status IN ('open', 'fixed', 'false_positive', 'accepted_risk', 'wont_fix')",
}


def _constraint_exists(table_name: str, constraint_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    constraints = inspector.get_check_constraints(table_name)
    return any(constraint.get("name") == constraint_name for constraint in constraints)


def upgrade() -> None:
    # Safety cleanup for environments where constraints were accidentally attached to users.
    for constraint_name, definition in FINDINGS_CHECK_CONSTRAINTS.items():
        if _constraint_exists("users", constraint_name):
            op.drop_constraint(constraint_name, "users", type_="check")

        # Ensure canonical constraints are present on findings.
        if not _constraint_exists("findings", constraint_name):
            op.create_check_constraint(constraint_name, "findings", definition)


def downgrade() -> None:
    # Intentionally a no-op to avoid dropping canonical findings constraints during rollback.
    pass
