"""add stats dayly

Revision ID: cdbd21d21e1c
Revises: 845f35e46a63
Create Date: 2024-11-03 08:12:44.269807

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cdbd21d21e1c'
down_revision: Union[str, None] = '845f35e46a63'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stats', sa.Column('dayly_goal', sa.Integer(), nullable=True))
    op.add_column('stats', sa.Column('last_day_learned', sa.Date(), nullable=True))
    op.add_column('stats', sa.Column('last_learn_count', sa.Integer(), nullable=True))
    op.drop_column('users', 'dayly_goal')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('dayly_goal', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('stats', 'last_learn_count')
    op.drop_column('stats', 'last_day_learned')
    op.drop_column('stats', 'dayly_goal')
    # ### end Alembic commands ###
