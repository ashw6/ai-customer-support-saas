"""Create uploaded documents table

Revision ID: b72e6d3a91c4
Revises: f15c2d4e9a10
Create Date: 2026-05-14

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b72e6d3a91c4"
down_revision: Union[str, Sequence[str], None] = "f15c2d4e9a10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "uploaded_documents",
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("text_length", sa.Integer(), nullable=False),
        sa.Column("chunk_count", sa.Integer(), nullable=False),
        sa.Column("uploaded_by_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["uploaded_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_uploaded_documents_id"), "uploaded_documents", ["id"], unique=False)
    op.create_index(
        op.f("ix_uploaded_documents_uploaded_by_id"),
        "uploaded_documents",
        ["uploaded_by_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_uploaded_documents_uploaded_by_id"), table_name="uploaded_documents")
    op.drop_index(op.f("ix_uploaded_documents_id"), table_name="uploaded_documents")
    op.drop_table("uploaded_documents")
