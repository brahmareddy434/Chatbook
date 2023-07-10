"""New Migration

Revision ID: 806afbd7b8e0
Revises: 
Create Date: 2023-07-07 20:23:45.084200

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '806afbd7b8e0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tabUser',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('firstname', sa.String(), nullable=True),
    sa.Column('lastname', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tabUser')
    # ### end Alembic commands ###