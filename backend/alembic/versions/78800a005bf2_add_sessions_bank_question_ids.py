"""add sessions bank_question_ids

Revision ID: 78800a005bf2
Revises: f819f153e1ce
Create Date: 2026-11-07 18:27:36.494045

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '78800a005bf2'
down_revision: Union[str, None] = 'f819f153e1ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('sessions', sa.Column('bank_question_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column('sessions', 'bank_question_ids')
