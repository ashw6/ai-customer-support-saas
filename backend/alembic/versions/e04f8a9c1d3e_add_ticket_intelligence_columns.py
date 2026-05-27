"""Add ticket intelligence columns (escalation, category, urgency, SLA, labels)

Revision ID: e04f8a9c1d3e
Revises: d93a7c1e4b2a
Create Date: 2026-05-14

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e04f8a9c1d3e"
down_revision: Union[str, Sequence[str], None] = "d93a7c1e4b2a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tickets",
        sa.Column(
            "is_escalated",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "tickets",
        sa.Column("category", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "tickets",
        sa.Column(
            "urgency_score",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
    )
    op.add_column(
        "tickets",
        sa.Column("sla_tag", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "tickets",
        sa.Column("smart_labels", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tickets", "smart_labels")
    op.drop_column("tickets", "sla_tag")
    op.drop_column("tickets", "urgency_score")
    op.drop_column("tickets", "category")
    op.drop_column("tickets", "is_escalated")
