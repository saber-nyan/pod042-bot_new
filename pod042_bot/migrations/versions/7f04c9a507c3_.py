"""empty message

Revision ID: 7f04c9a507c3
Revises: c58fb194c34b
Create Date: 2020-04-29 18:18:05.787466

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '7f04c9a507c3'
down_revision = 'c58fb194c34b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('chat_and_vk_group', 'chats_chat_id',
                    existing_type=sa.INTEGER(),
                    type_=sa.BigInteger(),
                    existing_nullable=True)
    op.alter_column('user_and_chat', 'chats_chat_id',
                    existing_type=sa.INTEGER(),
                    type_=sa.BigInteger(),
                    existing_nullable=True)
    op.alter_column('user_and_chat', 'users_user_id',
                    existing_type=sa.INTEGER(),
                    type_=sa.BigInteger(),
                    existing_nullable=True)
    op.alter_column('users', 'user_id',
                    existing_type=sa.INTEGER(),
                    type_=sa.BigInteger(),
                    autoincrement=True,
                    existing_server_default=sa.text("nextval('users_user_id_seq'::regclass)"))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'user_id',
                    existing_type=sa.BigInteger(),
                    type_=sa.INTEGER(),
                    autoincrement=True,
                    existing_server_default=sa.text("nextval('users_user_id_seq'::regclass)"))
    op.alter_column('user_and_chat', 'users_user_id',
                    existing_type=sa.BigInteger(),
                    type_=sa.INTEGER(),
                    existing_nullable=True)
    op.alter_column('user_and_chat', 'chats_chat_id',
                    existing_type=sa.BigInteger(),
                    type_=sa.INTEGER(),
                    existing_nullable=True)
    op.alter_column('chat_and_vk_group', 'chats_chat_id',
                    existing_type=sa.BigInteger(),
                    type_=sa.INTEGER(),
                    existing_nullable=True)
    # ### end Alembic commands ###
