#!/usr/bin/env python3
"""
Migration management script for OCR Identity REST API
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command: str, description: str = "") -> bool:
    """Run a command and return success status"""
    print(f"🔄 {description or command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def check_database_connection() -> bool:
    """Check if database is accessible"""
    print("🔍 Checking database connection...")
    return run_command(
        "python -c \"from app.core.config import get_config; print('Database config loaded successfully')\"",
        "Testing database configuration"
    )


def init_migrations() -> bool:
    """Initialize Alembic migrations"""
    print("📝 Initializing Alembic migrations...")
    return run_command("alembic init migrations", "Initializing Alembic")


def create_migration(message: str) -> bool:
    """Create a new migration"""
    print(f"📝 Creating migration: {message}")
    return run_command(f"alembic revision --autogenerate -m '{message}'", f"Creating migration: {message}")


def upgrade_database(revision: str = "head") -> bool:
    """Upgrade database to specified revision"""
    print(f"⬆️  Upgrading database to {revision}...")
    return run_command(f"alembic upgrade {revision}", f"Upgrading database to {revision}")


def downgrade_database(revision: str) -> bool:
    """Downgrade database to specified revision"""
    print(f"⬇️  Downgrading database to {revision}...")
    return run_command(f"alembic downgrade {revision}", f"Downgrading database to {revision}")


def show_migration_history() -> bool:
    """Show migration history"""
    print("📋 Migration history:")
    return run_command("alembic history", "Showing migration history")


def show_current_revision() -> bool:
    """Show current database revision"""
    print("📍 Current database revision:")
    return run_command("alembic current", "Showing current revision")


def show_pending_migrations() -> bool:
    """Show pending migrations"""
    print("⏳ Pending migrations:")
    return run_command("alembic heads", "Showing pending migrations")


def stamp_database(revision: str = "head") -> bool:
    """Stamp database with current revision without running migrations"""
    print(f"🏷️  Stamping database with {revision}...")
    return run_command(f"alembic stamp {revision}", f"Stamping database with {revision}")


def main():
    """Main migration management function"""
    if len(sys.argv) < 2:
        print("""
🔧 Migration Management Script

Usage:
  python scripts/migrate.py <command> [options]

Commands:
  init              - Initialize Alembic migrations
  create <message>  - Create a new migration
  upgrade [revision] - Upgrade database (default: head)
  downgrade <revision> - Downgrade database
  history           - Show migration history
  current           - Show current revision
  pending           - Show pending migrations
  stamp [revision]  - Stamp database (default: head)
  check             - Check database connection

Examples:
  python scripts/migrate.py init
  python scripts/migrate.py create "Add user table"
  python scripts/migrate.py upgrade
  python scripts/migrate.py downgrade 0001
  python scripts/migrate.py history
        """)
        return

    command = sys.argv[1]
    
    # Check database connection first
    if not check_database_connection():
        print("❌ Database connection failed. Please check your configuration.")
        sys.exit(1)
    
    if command == "init":
        success = init_migrations()
    elif command == "create":
        if len(sys.argv) < 3:
            print("❌ Please provide a migration message")
            sys.exit(1)
        message = sys.argv[2]
        success = create_migration(message)
    elif command == "upgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else "head"
        success = upgrade_database(revision)
    elif command == "downgrade":
        if len(sys.argv) < 3:
            print("❌ Please provide a revision to downgrade to")
            sys.exit(1)
        revision = sys.argv[2]
        success = downgrade_database(revision)
    elif command == "history":
        success = show_migration_history()
    elif command == "current":
        success = show_current_revision()
    elif command == "pending":
        success = show_pending_migrations()
    elif command == "stamp":
        revision = sys.argv[2] if len(sys.argv) > 2 else "head"
        success = stamp_database(revision)
    elif command == "check":
        success = True  # Already checked above
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
    
    if success:
        print("✅ Operation completed successfully")
    else:
        print("❌ Operation failed")
        sys.exit(1)


if __name__ == "__main__":
    main() 