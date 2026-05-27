"""Add sentiment column to tickets

Revision ID: c91e4b2a8f01
Revises: 825d71817189
Create Date: 2026-05-14

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c91e4b2a8f01"
down_revision: Union[str, Sequence[str], None] = "825d71817189"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tickets",
        sa.Column("sentiment", sa.String(length=20), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tickets", "sentiment")
