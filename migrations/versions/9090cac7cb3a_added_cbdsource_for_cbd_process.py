"""added cbdsource for cbd process

Revision ID: 9090cac7cb3a
Revises: 
Create Date: 2023-05-15 13:25:51.905481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9090cac7cb3a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appdata', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cbdsource', sa.String(length=20), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appdata', schema=None) as batch_op:
        batch_op.drop_column('cbdsource')

    # ### end Alembic commands ###
