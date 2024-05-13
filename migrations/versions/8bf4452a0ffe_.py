"""empty message

Revision ID: 8bf4452a0ffe
Revises: 838e28bfbcce
Create Date: 2023-11-08 08:21:34.131350

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8bf4452a0ffe'
down_revision = '838e28bfbcce'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('MoneyList',
    sa.Column('moneydata_id', sa.Integer(), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('value', sa.Integer(), nullable=False),
    sa.Column('sval', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['Group.id'], ),
    sa.PrimaryKeyConstraint('moneydata_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('MoneyList')
    # ### end Alembic commands ###