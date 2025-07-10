"""add_media_tables

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create media table
    op.create_table('media',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('hash', sa.String(length=255), nullable=True),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('disk', sa.String(length=255), nullable=False),
        sa.Column('mime_type', sa.String(length=255), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('record_left', sa.BigInteger(), nullable=True),
        sa.Column('record_right', sa.BigInteger(), nullable=True),
        sa.Column('record_dept', sa.BigInteger(), nullable=True),
        sa.Column('record_ordering', sa.BigInteger(), nullable=True),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('custom_attribute', sa.String(length=255), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('deleted_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('deleted_at', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['deleted_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['parent_id'], ['media.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create mediables table
    op.create_table('mediables',
        sa.Column('media_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('mediable_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('mediable_type', sa.String(length=255), nullable=False),
        sa.Column('group', sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(['media_id'], ['media.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('media_id', 'mediable_id')
    )
    
    # Create indexes for media table
    op.create_index(op.f('ix_media_name'), 'media', ['name'], unique=False)
    op.create_index(op.f('ix_media_file_name'), 'media', ['file_name'], unique=False)
    op.create_index(op.f('ix_media_hash'), 'media', ['hash'], unique=False)
    op.create_index(op.f('ix_media_parent_id'), 'media', ['parent_id'], unique=False)
    op.create_index(op.f('ix_media_created_by'), 'media', ['created_by'], unique=False)
    op.create_index(op.f('ix_media_updated_by'), 'media', ['updated_by'], unique=False)
    op.create_index(op.f('ix_media_deleted_by'), 'media', ['deleted_by'], unique=False)
    
    # Create indexes for mediables table
    op.create_index(op.f('ix_mediables_mediable_id'), 'mediables', ['mediable_id'], unique=False)
    op.create_index(op.f('ix_mediables_mediable_type'), 'mediables', ['mediable_type'], unique=False)
    op.create_index(op.f('ix_mediables_group'), 'mediables', ['group'], unique=False)
    op.create_index(op.f('ix_mediables_media_mediable'), 'mediables', ['media_id', 'mediable_id'], unique=False)
    op.create_index(op.f('ix_mediables_type_id'), 'mediables', ['mediable_type', 'mediable_id'], unique=False)


def downgrade() -> None:
    # Drop indexes for mediables table
    op.drop_index(op.f('ix_mediables_type_id'), table_name='mediables')
    op.drop_index(op.f('ix_mediables_media_mediable'), table_name='mediables')
    op.drop_index(op.f('ix_mediables_group'), table_name='mediables')
    op.drop_index(op.f('ix_mediables_mediable_type'), table_name='mediables')
    op.drop_index(op.f('ix_mediables_mediable_id'), table_name='mediables')
    
    # Drop indexes for media table
    op.drop_index(op.f('ix_media_deleted_by'), table_name='media')
    op.drop_index(op.f('ix_media_updated_by'), table_name='media')
    op.drop_index(op.f('ix_media_created_by'), table_name='media')
    op.drop_index(op.f('ix_media_parent_id'), table_name='media')
    op.drop_index(op.f('ix_media_hash'), table_name='media')
    op.drop_index(op.f('ix_media_file_name'), table_name='media')
    op.drop_index(op.f('ix_media_name'), table_name='media')
    
    # Drop tables
    op.drop_table('mediables')
    op.drop_table('media') 