"""
Logging API endpoints for viewing and managing application logs
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse
from app.core.logging_config import get_logger
from app.models.user import User

router = APIRouter(prefix="/logging", tags=["logging"])

logger = get_logger(__name__)


@router.get("/logs")
async def get_log_files() -> Dict[str, Any]:
    """Get list of available log files"""
    try:
        log_dir = Path("logs")
        if not log_dir.exists():
            return {"files": [], "message": "No logs directory found"}
        
        log_files = []
        for file_path in log_dir.glob("*.log"):
            stat = file_path.stat()
            log_files.append({
                "name": file_path.name,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "path": str(file_path)
            })
        
        # Sort by modification time (newest first)
        log_files.sort(key=lambda x: x["modified"], reverse=True)
        
        logger.info("Viewed log files")
        
        return {
            "files": log_files,
            "total_files": len(log_files)
        }
        
    except Exception as e:
        logger.error(f"Error getting log files: {e}")
        raise HTTPException(status_code=500, detail="Failed to get log files")


@router.get("/logs/{filename}")
async def get_log_content(
    filename: str,
    lines: Optional[int] = Query(default=100, ge=1, le=1000)
) -> Dict[str, Any]:
    """Get content of a specific log file"""
    try:
        log_dir = Path("logs")
        file_path = log_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Log file not found")
        
        if not filename.endswith('.log'):
            raise HTTPException(status_code=400, detail="Invalid log file")
        
        # Read last N lines
        with open(file_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            lines_to_read = lines if lines is not None else 100
            last_lines = all_lines[-lines_to_read:] if len(all_lines) > lines_to_read else all_lines
        
        logger.info(f"Viewed log file {filename}")
        
        return {
            "filename": filename,
            "total_lines": len(all_lines),
            "lines_requested": lines,
            "lines_returned": len(last_lines),
            "content": last_lines
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading log file {filename}: {e}")
        raise HTTPException(status_code=500, detail="Failed to read log file")


@router.get("/logs/{filename}/download")
async def download_log_file(
    filename: str
) -> FileResponse:
    """Download a log file"""
    try:
        log_dir = Path("logs")
        file_path = log_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Log file not found")
        
        if not filename.endswith('.log'):
            raise HTTPException(status_code=400, detail="Invalid log file")
        
        logger.info(f"Downloaded log file {filename}")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="text/plain"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading log file {filename}: {e}")
        raise HTTPException(status_code=500, detail="Failed to download log file")


@router.delete("/logs/{filename}")
async def delete_log_file(
    filename: str
) -> Dict[str, Any]:
    """Delete a log file"""
    try:
        log_dir = Path("logs")
        file_path = log_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Log file not found")
        
        if not filename.endswith('.log'):
            raise HTTPException(status_code=400, detail="Invalid log file")
        
        # Delete the file
        file_path.unlink()
        
        logger.info(f"Deleted log file {filename}")
        
        return {
            "message": f"Log file {filename} deleted successfully",
            "deleted_file": filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting log file {filename}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete log file")


@router.get("/stats")
async def get_log_stats() -> Dict[str, Any]:
    """Get logging statistics"""
    try:
        log_dir = Path("logs")
        if not log_dir.exists():
            return {"stats": {}, "message": "No logs directory found"}
        
        stats = {
            "total_files": 0,
            "total_size": 0,
            "file_types": {},
            "largest_file": None,
            "newest_file": None
        }
        
        largest_size = 0
        newest_time = 0
        
        for file_path in log_dir.glob("*.log"):
            stat = file_path.stat()
            file_size = stat.st_size
            
            stats["total_files"] += 1
            stats["total_size"] += file_size
            
            # Track file types
            file_type = file_path.name.split('.')[0] if '.' in file_path.name else "unknown"
            stats["file_types"][file_type] = stats["file_types"].get(file_type, 0) + 1
            
            # Track largest file
            if file_size > largest_size:
                largest_size = file_size
                stats["largest_file"] = {
                    "name": file_path.name,
                    "size": file_size
                }
            
            # Track newest file
            if stat.st_mtime > newest_time:
                newest_time = stat.st_mtime
                stats["newest_file"] = {
                    "name": file_path.name,
                    "modified": stat.st_mtime
                }
        
        logger.info("Viewed log statistics")
        
        return {"stats": stats}
        
    except Exception as e:
        logger.error(f"Error getting log stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get log statistics")


@router.post("/clear")
async def clear_logs() -> Dict[str, Any]:
    """Clear all log files (admin only)"""
    try:
        log_dir = Path("logs")
        if not log_dir.exists():
            return {"message": "No logs directory found"}
        
        deleted_count = 0
        for file_path in log_dir.glob("*.log"):
            file_path.unlink()
            deleted_count += 1
        
        logger.warning(f"Cleared all log files ({deleted_count} files)")
        
        return {
            "message": f"Cleared {deleted_count} log files",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error clearing logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear logs") 