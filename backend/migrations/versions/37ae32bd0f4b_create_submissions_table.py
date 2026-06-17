"""create_submissions_table

Revision ID: 37ae32bd0f4b
Revises: 98b8db8cb9ac
Create Date: 2026-06-17 03:18:05.720726

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql


# revision identifiers, used by Alembic.
revision: str = '37ae32bd0f4b'
down_revision: Union[str, Sequence[str], None] = '98b8db8cb9ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cria a tabela submissions para armazenar entregas de arquivos dos projetos."""
    op.create_table(
        "submissions",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("file_path", sa.String(1000), nullable=False),
        sa.Column("original_filename", sa.String(500), nullable=False),
        sa.Column("uploader_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("task_title", sa.String(255), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_index("ix_submissions_project_id", "submissions", ["project_id"])
    op.create_index("ix_submissions_uploader_id", "submissions", ["uploader_id"])


def downgrade() -> None:
    """Remove a tabela submissions."""
    op.drop_index("ix_submissions_uploader_id", table_name="submissions")
    op.drop_index("ix_submissions_project_id", table_name="submissions")
    op.drop_table("submissions")
