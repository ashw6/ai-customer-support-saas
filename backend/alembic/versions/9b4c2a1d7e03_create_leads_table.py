"""Create leads table

Revision ID: 9b4c2a1d7e03
Revises: b72e6d3a91c4
Create Date: 2026-05-14

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9b4c2a1d7e03"
down_revision: Union[str, Sequence[str], None] = "b72e6d3a91c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "leads",
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=40), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("matched_keyword", sa.String(length=80), nullable=True),
        sa.Column("source_message", sa.Text(), nullable=True),
        sa.Column("followup_sent", sa.Boolean(), nullable=False),
        sa.Column("captured_by_user_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["captured_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_leads_captured_by_user_id"), "leads", ["captured_by_user_id"], unique=False)
    op.create_index(op.f("ix_leads_email"), "leads", ["email"], unique=False)
    op.create_index(op.f("ix_leads_id"), "leads", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_leads_id"), table_name="leads")
    op.drop_index(op.f("ix_leads_email"), table_name="leads")
    op.drop_index(op.f("ix_leads_captured_by_user_id"), table_name="leads")
    op.drop_table("leads")
