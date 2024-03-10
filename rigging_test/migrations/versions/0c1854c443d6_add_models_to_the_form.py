"""Add models to the form

Revision ID: 0c1854c443d6
Revises: 0cc1cdeccfc6
Create Date: 2024-03-09 19:45:30.012898

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c1854c443d6'
down_revision = '0cc1cdeccfc6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('component', schema=None) as batch_op:
        batch_op.add_column(sa.Column('model_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'model', ['model_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('component', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('model_id')

    # ### end Alembic commands ###