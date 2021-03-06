"""empty message

Revision ID: 1d33547701ba
Revises: c9fc2c8cadfc
Create Date: 2019-05-14 21:27:49.459012

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d33547701ba'
down_revision = 'c9fc2c8cadfc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chats', sa.Column('state', sa.Integer(), nullable=False, server_default='0'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('chats', 'state')
    # ### end Alembic commands ###
