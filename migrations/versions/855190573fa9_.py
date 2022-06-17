"""empty message

Revision ID: 855190573fa9
Revises: d2e3fa0bbb03
Create Date: 2021-04-13 18:37:00.599782

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '855190573fa9'
down_revision = 'd2e3fa0bbb03'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('blog', schema=None) as batch_op:
        batch_op.add_column(sa.Column('describe', sa.Text(), nullable=True))
        batch_op.drop_column('discribe')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('blog', schema=None) as batch_op:
        batch_op.add_column(sa.Column('discribe', sa.TEXT(), nullable=True))
        batch_op.drop_column('describe')

    # ### end Alembic commands ###
