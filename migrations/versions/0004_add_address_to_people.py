"""add_people_addresses_table

Revision ID: 0004
Revises: 0002
Create Date: 2025-07-10 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'people_addresses',
        sa.Column('id', sa.String(length=26), primary_key=True),
        sa.Column('person_id', sa.String(length=26), nullable=False),
        sa.Column('address', sa.String(255), nullable=False),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('province', sa.String(100), nullable=True),
        sa.Column('postal_code', sa.String(20), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('created_by', sa.String(length=26), nullable=True),
        sa.Column('updated_by', sa.String(length=26), nullable=True),
        sa.Column('deleted_by', sa.String(length=26), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['person_id'], ['people.id'], name='fk_people_addresses_person_id', ondelete='CASCADE')
    )

def downgrade() -> None:
    op.drop_table('people_addresses')
