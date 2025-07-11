#!/usr/bin/env python3
"""
Test script for multi-database functionality
"""
import asyncio
import sys
import os
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.multi_database_utils import get_multi_database_utils
from app.core.database_session import multi_db_manager
from app.core.config import get_multi_database_config


def test_database_configuration():
    """Test database configuration loading"""
    print("🔧 Testing database configuration...")
    
    config = get_multi_database_config()
    
    # Check default database
    default_config = config.get_database_config("default")
    print(f"   ✅ Default database: {default_config.host}:{default_config.port}/{default_config.database}")
    
    # Check analytics database
    analytics_config = config.get_database_config("analytics")
    if analytics_config:
        print(f"   ✅ Analytics database: {analytics_config.host}:{analytics_config.port}/{analytics_config.database}")
    else:
        print("   ⚠️  Analytics database not configured")
    
    # Check logging database
    logging_config = config.get_database_config("logging")
    if logging_config:
        print(f"   ✅ Logging database: {logging_config.host}:{logging_config.port}/{logging_config.database}")
    else:
        print("   ⚠️  Logging database not configured")
    
    # Check archive database
    archive_config = config.get_database_config("archive")
    if archive_config:
        print(f"   ✅ Archive database: {archive_config.host}:{archive_config.port}/{archive_config.database}")
    else:
        print("   ⚠️  Archive database not configured")
    
    return True


def test_database_connections():
    """Test database connections"""
    print("\n🔌 Testing database connections...")
    
    utils = get_multi_database_utils()
    databases = utils.get_configured_databases()
    
    for db_name in databases:
        try:
            engine = multi_db_manager.get_engine(db_name)
            with engine.connect() as conn:
                result = conn.execute("SELECT 1 as test")
                test_result = result.fetchone()
                print(f"   ✅ {db_name}: Connected successfully (test query: {test_result[0]})")
        except Exception as e:
            print(f"   ❌ {db_name}: Connection failed - {str(e)}")
            return False
    
    return True


def test_health_checks():
    """Test health checks"""
    print("\n🏥 Testing health checks...")
    
    utils = get_multi_database_utils()
    health_status = utils.health_check_all_databases()
    
    for db_name, status in health_status.items():
        if status.get("status") == "healthy":
            print(f"   ✅ {db_name}: {status.get('database_name', 'Unknown')} - {status.get('version', 'Unknown')}")
        else:
            print(f"   ❌ {db_name}: {status.get('error', 'Unknown error')}")
    
    return all(status.get("status") == "healthy" for status in health_status.values())


def test_database_statistics():
    """Test database statistics"""
    print("\n📊 Testing database statistics...")
    
    utils = get_multi_database_utils()
    stats = utils.get_all_database_stats()
    
    for db_name, stat in stats.items():
        if stat.get("status") == "available":
            print(f"   ✅ {db_name}: {stat.get('table_count', 0)} tables, {stat.get('database_size', 'Unknown')}")
        else:
            print(f"   ❌ {db_name}: {stat.get('error', 'Unknown error')}")
    
    return all(stat.get("status") == "available" for stat in stats.values())


def test_model_routing():
    """Test model routing"""
    print("\n🛣️  Testing model routing...")
    
    utils = get_multi_database_utils()
    model_groups = utils.get_models_by_database()
    
    for db_name, models in model_groups.items():
        print(f"   📋 {db_name}: {', '.join(models)}")
    
    return len(model_groups) > 0


def test_query_execution():
    """Test query execution"""
    print("\n🔍 Testing query execution...")
    
    utils = get_multi_database_utils()
    databases = utils.get_configured_databases()
    
    for db_name in databases:
        try:
            result = utils.execute_on_database(db_name, "SELECT current_database() as db_name")
            if result:
                db_name_result = result[0][0] if result[0] else "Unknown"
                print(f"   ✅ {db_name}: Query executed successfully (database: {db_name_result})")
            else:
                print(f"   ⚠️  {db_name}: Query executed but no result")
        except Exception as e:
            print(f"   ❌ {db_name}: Query execution failed - {str(e)}")
            return False
    
    return True


def test_backup_information():
    """Test backup information"""
    print("\n💾 Testing backup information...")
    
    utils = get_multi_database_utils()
    backup_info = utils.backup_database_info()
    
    for db_name, info in backup_info.items():
        print(f"   📋 {db_name}: {info.get('host', 'Unknown')}:{info.get('port', 'Unknown')}/{info.get('database', 'Unknown')}")
    
    return len(backup_info) > 0


def main():
    """Run all tests"""
    print("🚀 Starting Multi-Database Tests")
    print("=" * 50)
    
    tests = [
        ("Database Configuration", test_database_configuration),
        ("Database Connections", test_database_connections),
        ("Health Checks", test_health_checks),
        ("Database Statistics", test_database_statistics),
        ("Model Routing", test_model_routing),
        ("Query Execution", test_query_execution),
        ("Backup Information", test_backup_information),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ {test_name}: Test failed with exception - {str(e)}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Multi-database functionality is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration and database connections.")
        return 1


if __name__ == "__main__":
    exit(main()) 