"""add messages bank_question_id

Revision ID: f819f153e1ce
Revises: 95d32ffa6d6b
Create Date: 2026-11-03 21:57:50.678276

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f819f153e1ce'
down_revision: Union[str, None] = '95d32ffa6d6b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('messages', sa.Column('bank_question_id', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('messages', 'bank_question_id')
