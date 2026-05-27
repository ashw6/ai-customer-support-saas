"""Add ai_reply column to tickets

Revision ID: d93a7c1e4b2a
Revises: c91e4b2a8f01
Create Date: 2026-05-14

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d93a7c1e4b2a"
down_revision: Union[str, Sequence[str], None] = "c91e4b2a8f01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tickets",
        sa.Column("ai_reply", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tickets", "ai_reply")
