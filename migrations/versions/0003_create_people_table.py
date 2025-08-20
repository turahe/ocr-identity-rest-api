"""create_people_table_with_uuid

Revision ID: 76af02c73823
Revises: 0002
Create Date: 2025-07-10 13:15:53.367131

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create people table with UUID fields
    op.create_table(
        'people',
        sa.Column('id', sa.String(length=26), primary_key=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('place_of_birth', sa.String(255), nullable=True),
        sa.Column('date_of_birth', sa.Date, nullable=True),
        sa.Column('gender', sa.String(30), nullable=False, server_default='UNDEFINED'),
        sa.Column('religion', sa.String(30), nullable=False, server_default='UNDEFINED'),
        sa.Column('citizenship_identity', sa.String(255), nullable=False),
        sa.Column('citizenship', sa.String(30), nullable=False, server_default='UNDEFINED'),
        sa.Column('nationality', sa.String(255), nullable=False, server_default='UNDEFINED'),
        sa.Column('ethnicity', sa.String(255), nullable=True),
        sa.Column('marital_status', sa.String(30), nullable=False, server_default='UNDEFINED'),
        sa.Column('disability_status', sa.Integer, nullable=False, server_default='0'),
        sa.Column('blood_type', sa.String(255), nullable=True),
        sa.Column('job', sa.String(255), nullable=True),
        sa.Column('created_by', sa.String(length=26), nullable=True),
        sa.Column('updated_by', sa.String(length=26), nullable=True),
        sa.Column('deleted_by', sa.String(length=26), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        # Foreign key constraints
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_people_created_by'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name='fk_people_updated_by'),
        sa.ForeignKeyConstraint(['deleted_by'], ['users.id'], name='fk_people_deleted_by'),
        
        # Check constraints
        sa.CheckConstraint(
            "gender IN ('MALE', 'FEMALE', 'UNDEFINED')",
            name='check_gender_valid'
        ),
        sa.CheckConstraint(
            "religion IN ('HINDU', 'BUDDHA', 'MUSLIM', 'CHRISTIAN', 'CATHOLIC', 'CONFUCIUS', 'UNDEFINED')",
            name='check_religion_valid'
        ),
        sa.CheckConstraint(
            "citizenship IN ('INDONESIAN_CITIZEN', 'INDONESIAN_DESCENT_CITIZEN', 'ORIGINAL_INDONESIAN_CITIZEN', 'DUAL_INDONESIAN_CITIZEN', 'STATELESS_INDONESIAN_CITIZEN', 'UNDEFINED')",
            name='check_citizenship_valid'
        ),
        sa.CheckConstraint(
            "marital_status IN ('SINGLE', 'MARRIED', 'DIVORCED', 'SEPARATED', 'WIDOWED', 'ANNULLED', 'CIVIL_DOMESTIC_PARTNERSHIP', 'COMMON_LOW_MARRIAGE', 'ENGAGED', 'COMPLICATED', 'UNDEFINED')",
            name='check_marital_status_valid'
        ),
        sa.CheckConstraint(
            "disability_status > 0",
            name='check_disability_status_positive'
        ),
    )
    
    # Create indexes for better performance
    op.create_index('idx_people_full_name', 'people', ['full_name'])
    op.create_index('idx_people_citizenship_identity', 'people', ['citizenship_identity'])
    op.create_index('idx_people_gender', 'people', ['gender'])
    op.create_index('idx_people_religion', 'people', ['religion'])
    op.create_index('people_created_at_idx', 'people', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('people_created_at_idx', table_name='people')
    op.drop_index('idx_people_religion', table_name='people')
    op.drop_index('idx_people_gender', table_name='people')
    op.drop_index('idx_people_citizenship_identity', table_name='people')
    op.drop_index('idx_people_full_name', table_name='people')
    
    # Drop table
    op.drop_table('people') 