#!/usr/bin/env python3
"""
Celery worker startup script
"""
import os
import sys
import argparse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.celery_app import celery_app


def start_worker(queue: str = "default", concurrency: int = 4, log_level: str = "INFO"):
    """Start Celery worker"""
    print(f"Starting Celery worker for queue: {queue}")
    print(f"Concurrency: {concurrency}")
    print(f"Log level: {log_level}")
    
    # Start worker
    celery_app.worker_main([
        "worker",
        "--loglevel", log_level,
        "--concurrency", str(concurrency),
        "--queues", queue,
        "--hostname", f"worker@{queue}",
        "--without-gossip",
        "--without-mingle",
        "--without-heartbeat"
    ])


def start_beat():
    """Start Celery beat scheduler"""
    print("Starting Celery beat scheduler")
    
    celery_app.worker_main([
        "beat",
        "--loglevel", "INFO",
        "--scheduler", "celery.beat.PersistentScheduler"
    ])


def main():
    parser = argparse.ArgumentParser(description="Start Celery worker or beat")
    parser.add_argument("--worker", action="store_true", help="Start worker")
    parser.add_argument("--beat", action="store_true", help="Start beat scheduler")
    parser.add_argument("--queue", default="default", help="Queue name")
    parser.add_argument("--concurrency", type=int, default=4, help="Number of worker processes")
    parser.add_argument("--log-level", default="INFO", help="Log level")
    
    args = parser.parse_args()
    
    if args.beat:
        start_beat()
    elif args.worker:
        start_worker(args.queue, args.concurrency, args.log_level)
    else:
        print("Please specify --worker or --beat")
        sys.exit(1)


if __name__ == "__main__":
    main() 