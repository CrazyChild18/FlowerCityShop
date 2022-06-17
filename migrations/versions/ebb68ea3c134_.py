"""empty message

Revision ID: ebb68ea3c134
Revises: 
Create Date: 2021-05-11 17:14:00.927663

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ebb68ea3c134'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blog_pic',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pic', sa.String(), nullable=True),
    sa.Column('blog_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['blog_id'], ['blog.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('blog_pic', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_blog_pic_pic'), ['pic'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('blog_pic', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_blog_pic_pic'))

    op.drop_table('blog_pic')
    # ### end Alembic commands ###
