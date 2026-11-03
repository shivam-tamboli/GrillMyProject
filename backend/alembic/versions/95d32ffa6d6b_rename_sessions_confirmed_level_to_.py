"""rename sessions confirmed_level to current_level

Revision ID: 95d32ffa6d6b
Revises: 1b916bf5256a
Create Date: 2026-11-03 16:38:37.485778

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95d32ffa6d6b'
down_revision: Union[str, None] = '1b916bf5256a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('sessions', 'confirmed_level', new_column_name='current_level')


def downgrade() -> None:
    op.alter_column('sessions', 'current_level', new_column_name='confirmed_level')
