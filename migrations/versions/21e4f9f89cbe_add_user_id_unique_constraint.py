"""add user_id unique constraint

Revision ID: 21e4f9f89cbe
Revises: d910a6d08f13
Create Date: 2025-01-01 00:31:55.810386

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '21e4f9f89cbe'
down_revision: Union[str, None] = 'd910a6d08f13'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'projectaccess', ['user_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'projectaccess', type_='unique')
    # ### end Alembic commands ###
