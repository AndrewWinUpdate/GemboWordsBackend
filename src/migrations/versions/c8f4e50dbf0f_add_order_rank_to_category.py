"""add order rank to category

Revision ID: c8f4e50dbf0f
Revises: 961c49780d59
Create Date: 2024-10-20 01:55:35.289787

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8f4e50dbf0f'
down_revision: Union[str, None] = '961c49780d59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('categories', sa.Column('sort_order', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('categories', 'sort_order')
    # ### end Alembic commands ###