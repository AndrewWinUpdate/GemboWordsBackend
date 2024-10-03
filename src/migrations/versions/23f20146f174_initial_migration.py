"""Initial migration

Revision ID: 23f20146f174
Revises: 
Create Date: 2024-10-02 23:20:20.182932

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23f20146f174'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('creation_date', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('categories',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('picture', sa.String(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('examples',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('text', sa.String(), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('stats',
    sa.Column('user_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('learned_words', sa.Integer(), nullable=False),
    sa.Column('learning_words', sa.Integer(), nullable=False),
    sa.Column('known_words', sa.Integer(), nullable=False),
    sa.Column('problematic_words', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('words',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('english', sa.String(), nullable=False),
    sa.Column('russian', sa.String(), nullable=False),
    sa.Column('transcription', sa.String(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_category_association',
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('category_id', 'user_id')
    )
    op.create_table('user_word_relations',
    sa.Column('word_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('state', sa.Integer(), nullable=False),
    sa.Column('repeat_iteration', sa.Integer(), nullable=False),
    sa.Column('next_repeat', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['word_id'], ['words.id'], ),
    sa.PrimaryKeyConstraint('word_id', 'user_id')
    )
    op.create_table('word_category_association',
    sa.Column('word_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['word_id'], ['words.id'], ),
    sa.PrimaryKeyConstraint('word_id', 'category_id')
    )
    op.create_table('word_example_association',
    sa.Column('word_id', sa.Integer(), nullable=False),
    sa.Column('example_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['example_id'], ['examples.id'], ),
    sa.ForeignKeyConstraint(['word_id'], ['words.id'], ),
    sa.PrimaryKeyConstraint('word_id', 'example_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('word_example_association')
    op.drop_table('word_category_association')
    op.drop_table('user_word_relations')
    op.drop_table('user_category_association')
    op.drop_table('words')
    op.drop_table('stats')
    op.drop_table('examples')
    op.drop_table('categories')
    op.drop_table('users')
    # ### end Alembic commands ###
