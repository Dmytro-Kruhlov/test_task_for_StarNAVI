"""Add cascade delete-orphan

Revision ID: e8e284e49ed9
Revises: 9013e49d9c89
Create Date: 2024-08-03 13:19:24.459668

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8e284e49ed9'
down_revision: Union[str, None] = '9013e49d9c89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
