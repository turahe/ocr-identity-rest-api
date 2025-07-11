"""
Database management API endpoints
"""
from typing import Dict, Any, List, Union, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database_session import get_db
from app.core.multi_database_utils import (
    get_multi_database_utils,
    health_check_all,
    get_database_stats_all,
    get_configured_databases,
    get_models_by_database
)
from app.api.auth import get_current_user_or_apikey
from app.models.user import User

router = APIRouter(prefix="/database", tags=["database"])


@router.get("/health", summary="Health check all databases")
async def health_check_databases(
    current_user: Union[User, Dict[str, str]] = Depends(get_current_user_or_apikey)
) -> Dict[str, Dict[str, Any]]:
    """
    Perform health check on all configured databases.
    
    Returns:
        Dictionary with database health status for each configured database
    """
    return health_check_all()


@router.get("/stats", summary="Get statistics for all databases")
async def get_database_statistics(
    current_user: Union[User, Dict[str, str]] = Depends(get_current_user_or_apikey)
) -> Dict[str, Dict[str, Any]]:
    """
    Get statistics for all configured databases.
    
    Returns:
        Dictionary with database statistics for each configured database
    """
    return get_database_stats_all()


@router.get("/configured", summary="Get list of configured databases")
async def get_databases(
    current_user: Union[User, Dict[str, str]] = Depends(get_current_user_or_apikey)
) -> Dict[str, List[str]]:
    """
    Get list of all configured databases.
    
    Returns:
        Dictionary with list of configured database names
    """
    databases = get_configured_databases()
    return {"databases": databases}


@router.get("/models", summary="Get models grouped by database")
async def get_models_by_database_endpoint(
    current_user: Union[User, Dict[str, str]] = Depends(get_current_user_or_apikey)
) -> Dict[str, List[str]]:
    """
    Get models grouped by their assigned databases.
    
    Returns:
        Dictionary with models grouped by database name
    """
    return get_models_by_database()


@router.get("/{database_name}/health", summary="Health check specific database")
async def health_check_specific_database(
    database_name: str,
    current_user: Union[User, Dict[str, str]] = Depends(get_current_user_or_apikey)
) -> Dict[str, Any]:
    """
    Perform health check on specific database.
    
    Args:
        database_name: Name of the database to check
        
    Returns:
        Health status of the specified database
    """
    utils = get_multi_database_utils()
    
    if database_name not in get_configured_databases():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database '{database_name}' not found or not configured"
        )
    
    return utils.health_check_database(database_name)


@router.get("/{database_name}/stats", summary="Get statistics for specific database")
async def get_database_statistics_specific(
    database_name: str,
    current_user: Union[User, Dict[str, str]] = Depends(get_current_user_or_apikey)
) -> Dict[str, Any]:
    """
    Get statistics for specific database.
    
    Args:
        database_name: Name of the database to get stats for
        
    Returns:
        Statistics for the specified database
    """
    utils = get_multi_database_utils()
    
    if database_name not in get_configured_databases():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database '{database_name}' not found or not configured"
        )
    
    return utils.get_database_stats(database_name)


@router.get("/{database_name}/models", summary="Get models for specific database")
async def get_models_for_database(
    database_name: str,
    current_user: Union[User, Dict[str, str]] = Depends(get_current_user_or_apikey)
) -> Dict[str, Any]:
    """
    Get models assigned to specific database.
    
    Args:
        database_name: Name of the database to get models for
        
    Returns:
        List of models assigned to the specified database
    """
    utils = get_multi_database_utils()
    
    if database_name not in get_configured_databases():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database '{database_name}' not found or not configured"
        )
    
    models = utils.router.get_models_for_database(database_name)
    return {"database": database_name, "models": models}


@router.post("/{database_name}/execute", summary="Execute query on specific database")
async def execute_query_on_database(
    database_name: str,
    query: str,
    params: Optional[Dict[str, Any]] = None,
    current_user: Union[User, Dict[str, str]] = Depends(get_current_user_or_apikey)
) -> Dict[str, Any]:
    """
    Execute a query on specific database.
    
    Args:
        database_name: Name of the database to execute query on
        query: SQL query to execute
        params: Query parameters (optional)
        
    Returns:
        Query results from the specified database
    """
    utils = get_multi_database_utils()
    
    if database_name not in get_configured_databases():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database '{database_name}' not found or not configured"
        )
    
    try:
        result = utils.execute_on_database(database_name, query, params or {})
        return {
            "database": database_name,
            "query": query,
            "params": params,
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing query on {database_name}: {str(e)}"
        )


@router.get("/backup/info", summary="Get backup information for all databases")
async def get_backup_information(
    current_user: Union[User, Dict[str, str]] = Depends(get_current_user_or_apikey)
) -> Dict[str, Any]:
    """
    Get backup information for all configured databases.
    
    Returns:
        Backup information for all databases
    """
    utils = get_multi_database_utils()
    return utils.backup_database_info() 