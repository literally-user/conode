"""unique-username-email

Revision ID: 807cb62be0ae
Revises: b210c4de87de
Create Date: 2026-08-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '807cb62be0ae'
down_revision: Union[str, Sequence[str], None] = 'b210c4de87de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint('uq_user_record_username', 'user_record', ['username'])
    op.create_unique_constraint('uq_user_record_email', 'user_record', ['email'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_user_record_email', 'user_record', type_='unique')
    op.drop_constraint('uq_user_record_username', 'user_record', type_='unique')
