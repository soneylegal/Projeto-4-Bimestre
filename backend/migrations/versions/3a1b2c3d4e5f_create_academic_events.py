"""create academic_events table

Revision ID: 3a1b2c3d4e5f
Revises: b6281ee61401
Create Date: 2026-06-26 17:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '3a1b2c3d4e5f'
down_revision: Union[str, None] = 'b6281ee61401'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'academic_events',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.String(1000), nullable=True),
        sa.Column('event_date', sa.DateTime(), nullable=False, index=True),
        sa.Column('event_type', sa.String(20), nullable=False, server_default='academic'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('academic_events')
