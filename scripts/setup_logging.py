#!/usr/bin/env python3
"""
Setup and test logging configuration for OCR Identity REST API
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.logging_config import setup_logging, get_logger
from app.core.config import get_config


def test_logging_setup():
    """Test the logging setup"""
    print("🧪 Testing logging configuration...")
    
    # Setup logging
    setup_logging()
    
    # Get logger
    logger = get_logger("test_logging")
    
    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    print("✅ Logging test completed")


def check_log_files():
    """Check if log files are being created"""
    print("📁 Checking log files...")
    
    log_dir = Path("logs")
    if not log_dir.exists():
        print("❌ Logs directory does not exist")
        return False
    
    log_files = list(log_dir.glob("*.log"))
    if not log_files:
        print("❌ No log files found")
        return False
    
    print(f"✅ Found {len(log_files)} log files:")
    for log_file in log_files:
        size = log_file.stat().st_size
        print(f"   - {log_file.name} ({size} bytes)")
    
    return True


def test_logging_configuration():
    """Test logging configuration"""
    print("🔧 Testing logging configuration...")
    
    config = get_config()
    print(f"Environment: {config.environment}")
    print(f"Debug mode: {config.debug}")
    
    # Test different loggers
    loggers_to_test = [
        "app",
        "app.api",
        "app.core",
        "app.services",
        "app.tasks",
        "app.models",
        "uvicorn",
        "fastapi",
        "sqlalchemy",
        "celery"
    ]
    
    for logger_name in loggers_to_test:
        logger = get_logger(logger_name)
        logger.info(f"Test message from {logger_name}")
    
    print("✅ Logging configuration test completed")


def create_sample_logs():
    """Create sample log entries for testing"""
    print("📝 Creating sample log entries...")
    
    setup_logging()
    
    # Test different components
    api_logger = get_logger("app.api")
    service_logger = get_logger("app.services")
    task_logger = get_logger("app.tasks")
    db_logger = get_logger("app.database")
    
    # API logs
    api_logger.info("GET /health - Status: 200 - Time: 0.002s")
    api_logger.info("POST /auth/login - Status: 200 - Time: 0.150s")
    api_logger.error("GET /invalid - Status: 404 - Time: 0.001s")
    
    # Service logs
    service_logger.info("S3 upload: test-image.jpg (1.2MB) - completed in 0.5s")
    service_logger.info("Redis get: user_session_123 - completed in 0.001s")
    service_logger.error("Email send failed: Connection timeout")
    
    # Task logs
    task_logger.info("Celery task: process_ocr_image started - task_id: abc123")
    task_logger.info("Celery task: process_ocr_image completed - task_id: abc123 - duration: 2.5s")
    task_logger.error("Celery task: process_ocr_image failed - task_id: abc123 - error: Model not found")
    
    # Database logs
    db_logger.info("Database transaction: SELECT users - completed in 0.003s")
    db_logger.info("Database transaction: INSERT media - completed in 0.008s")
    db_logger.error("Database error: Connection lost")
    
    print("✅ Sample log entries created")


def main():
    """Main function"""
    print("🚀 OCR Identity REST API - Logging Setup")
    print("=" * 50)
    
    try:
        # Test logging setup
        test_logging_setup()
        print()
        
        # Test configuration
        test_logging_configuration()
        print()
        
        # Create sample logs
        create_sample_logs()
        print()
        
        # Check log files
        if check_log_files():
            print("\n🎉 Logging setup completed successfully!")
            print("\n📋 Log files created:")
            print("   - app.log: Application logs")
            print("   - error.log: Error logs")
            print("   - access.log: API access logs")
            print("\n🔍 You can view logs via:")
            print("   - API: GET /logging/logs")
            print("   - Direct: tail -f logs/app.log")
            print("   - Download: GET /logging/logs/app.log/download")
        else:
            print("\n❌ Logging setup failed")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error during logging setup: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 