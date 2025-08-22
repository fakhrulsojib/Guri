import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog

PG_HOST = os.environ.get("POSTGRES_HOST", "db")
PG_DB = os.environ.get("POSTGRES_DB", "postgres")
PG_USER = os.environ.get("POSTGRES_USER", "postgres")
PG_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "password69")

logger = structlog.get_logger()

def get_connection():
    return psycopg2.connect(
        host=PG_HOST,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD
    )

def execute_query(query: str, params: Optional[tuple] = None) -> None:
    logger.debug("Executing database query", query=query, params=params)
    
    conn = get_connection()
    cur = conn.cursor()
    try:
        if params is not None:
            if query.count('%s') != len(params):
                logger.error("Parameter count mismatch", param_count=len(params), placeholder_count=query.count('%s'))
                raise ValueError(f"Parameter count ({len(params)}) does not match placeholders ({query.count('%s')})")
            cur.execute(query, params)
        else:
            cur.execute(query)
        conn.commit()
        logger.debug("Database query executed successfully")
    except Exception as e:
        logger.error("Database query execution failed", query=query, params=params, error=str(e))
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def execute_query_with_result(query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    logger.debug("Executing database query with result", query=query, params=params)
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        if params is not None:
            if query.count('%s') != len(params):
                logger.error("Parameter count mismatch", param_count=len(params), placeholder_count=query.count('%s'))
                raise ValueError(f"Parameter count ({len(params)}) does not match placeholders ({query.count('%s')})")
            cur.execute(query, params)
        else:
            cur.execute(query)
        
        conn.commit()
        
        results = cur.fetchall()
        logger.debug("Database query executed successfully", result_count=len(results))
        return [dict(row) for row in results]
    except Exception as e:
        logger.error("Database query execution failed", query=query, params=params, error=str(e))
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def execute_query_single_result(query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
    results = execute_query_with_result(query, params)
    return results[0] if results else None

def check_database_connection() -> bool:
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logger.error("Database connection failed", error=str(e))
        return False 