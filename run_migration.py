#!/usr/bin/env python3
"""
Simple script to run database migration
"""
import os
import sys
import tempfile
import shutil

# Set required environment variables
os.environ.setdefault('AWS_ACCESS_KEY_ID', 'minioadmin')
os.environ.setdefault('AWS_SECRET_ACCESS_KEY', 'minioadmin')
os.environ.setdefault('S3_BUCKET_NAME', 'ocr-identity-bucket')
os.environ.setdefault('SECRET_KEY', 'dev-secret-key')
os.environ.setdefault('EMAIL_USERNAME', 'test@example.com')
os.environ.setdefault('EMAIL_PASSWORD', '')
os.environ.setdefault('EMAIL_FROM', 'test@example.com')

def run_migration():
    """Run the database migration"""
    try:
        # Temporarily modify the config to make S3 optional
        config_file = "app/core/config.py"
        backup_file = "app/core/config.py.bak"
        
        # Create backup
        shutil.copy2(config_file, backup_file)
        
        # Read the config file
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Temporarily make S3 fields optional
        modified_content = content.replace(
            'aws_access_key_id: str = Field(..., env="AWS_ACCESS_KEY_ID")',
            'aws_access_key_id: str = Field(default="", env="AWS_ACCESS_KEY_ID")'
        ).replace(
            'aws_secret_access_key: str = Field(..., env="AWS_SECRET_ACCESS_KEY")',
            'aws_secret_access_key: str = Field(default="", env="AWS_SECRET_ACCESS_KEY")'
        ).replace(
            'bucket_name: str = Field(..., env="S3_BUCKET_NAME")',
            'bucket_name: str = Field(default="", env="S3_BUCKET_NAME")'
        )
        
        # Write modified content
        with open(config_file, 'w') as f:
            f.write(modified_content)
        
        try:
            from alembic.config import Config
            from alembic import command
            
            # Create Alembic configuration
            alembic_cfg = Config("alembic.ini")
            
            # Run the migration
            print("Running database migration...")
            command.upgrade(alembic_cfg, "head")
            print("✅ Migration completed successfully!")
            
        finally:
            # Restore original config
            shutil.move(backup_file, config_file)
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration() 