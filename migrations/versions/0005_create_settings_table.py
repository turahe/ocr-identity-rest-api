"""create_settings_table

Revision ID: 0005
Revises: 0004
Create Date: 2024-07-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'settings',
        sa.Column('id', sa.String(length=26), nullable=False),
        sa.Column('model_type', sa.String(length=255), nullable=True),
        sa.Column('model_id', sa.String(length=26), nullable=True),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('value', sa.String(length=255), nullable=True),
        sa.Column('created_by', sa.String(length=26), nullable=True),
        sa.Column('updated_by', sa.String(length=26), nullable=True),
        sa.Column('deleted_by', sa.String(length=26), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='setting_created_by_foreign', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name='setting_updated_by_foreign', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['deleted_by'], ['users.id'], name='setting_deleted_by_foreign', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name='setting_pkey')
    )

def downgrade() -> None:
    op.drop_table('settings') 