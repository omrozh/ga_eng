"""empty message

Revision ID: c0f20ef58369
Revises: 
Create Date: 2023-02-25 10:09:57.656986

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0f20ef58369'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('interest_obj')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('interest_obj',
    sa.Column('id', sa.VARCHAR(), nullable=False),
    sa.Column('user_fk', sa.VARCHAR(), nullable=True),
    sa.Column('last_twenty_interacted_tags', sa.VARCHAR(), nullable=True),
    sa.Column('following_tags', sa.VARCHAR(), nullable=True),
    sa.Column('following_creators', sa.VARCHAR(), nullable=True),
    sa.Column('most_common_keywords', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
