#!/usr/bin/env python3
"""
Test runner script for OCR Identity REST API

Usage:
    python scripts/run_tests.py                    # Run all tests
    python scripts/run_tests.py --unit            # Run unit tests only
    python scripts/run_tests.py --integration     # Run integration tests only
    python scripts/run_tests.py --coverage        # Run with coverage report
    python scripts/run_tests.py --watch           # Run in watch mode
    python scripts/run_tests.py --verbose         # Run with verbose output
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(args):
    """Run tests with specified arguments"""
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test path
    cmd.append("tests/")
    
    # Add options based on arguments
    if args.unit:
        cmd.extend(["-k", "TestMediaModel or TestMediableModel or TestMediaManager"])
    
    if args.integration:
        cmd.extend(["-k", "TestMediaWorkflow or TestDatabaseOperations"])
    
    if args.coverage:
        cmd.extend([
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html",
            "--cov-fail-under=80"
        ])
    
    if args.watch:
        cmd = ["python", "-m", "pytest-watch", "--", "tests/"]
    
    if args.verbose:
        cmd.append("-v")
    
    if args.fast:
        cmd.extend(["-x", "--tb=short"])
    
    # Add additional pytest options
    if args.pytest_args:
        cmd.extend(args.pytest_args)
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ Tests passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return e.returncode


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Run tests for OCR Identity REST API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_tests.py                    # Run all tests
  python scripts/run_tests.py --unit            # Run unit tests only
  python scripts/run_tests.py --integration     # Run integration tests only
  python scripts/run_tests.py --coverage        # Run with coverage report
  python scripts/run_tests.py --watch           # Run in watch mode
  python scripts/run_tests.py --verbose         # Run with verbose output
  python scripts/run_tests.py --fast            # Stop on first failure
        """
    )
    
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run unit tests only"
    )
    
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run integration tests only"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage report"
    )
    
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Run in watch mode (auto-rerun on file changes)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Run with verbose output"
    )
    
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Stop on first failure"
    )
    
    parser.add_argument(
        "pytest_args",
        nargs="*",
        help="Additional pytest arguments"
    )
    
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not Path("tests/").exists():
        print("❌ Error: tests/ directory not found. Please run from project root.")
        return 1
    
    # Check if pytest is installed
    try:
        subprocess.run(["python", "-m", "pytest", "--version"], 
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("❌ Error: pytest not found. Please install testing dependencies:")
        print("pip install -r requirements.txt")
        return 1
    
    return run_tests(args)


if __name__ == "__main__":
    sys.exit(main()) 