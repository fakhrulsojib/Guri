import os
import asyncio
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog

try:
    import asyncpg
except ImportError:
    asyncpg = None

PG_HOST = os.environ.get("POSTGRES_HOST", "db")
PG_DB = os.environ.get("POSTGRES_DB", "postgres")
PG_USER = os.environ.get("POSTGRES_USER", "postgres")
PG_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "password69")

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# Async connection pool (asyncpg) – used by FastAPI HTTP handlers
# ---------------------------------------------------------------------------

_pool: Optional["asyncpg.Pool"] = None


async def init_db_pool(min_size: int = 5, max_size: int = 20) -> None:
    """Create the asyncpg connection pool. Call once at application startup."""
    global _pool
    if _pool is not None:
        return

    _pool = await asyncpg.create_pool(
        host=PG_HOST,
        database=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
        min_size=min_size,
        max_size=max_size,
    )
    logger.info("Async database pool created", min_size=min_size, max_size=max_size)


async def close_db_pool() -> None:
    """Close the asyncpg connection pool. Call once at application shutdown."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("Async database pool closed")


def _get_pool() -> "asyncpg.Pool":
    """Return the active pool or raise if not initialised."""
    if _pool is None:
        raise RuntimeError("Database pool is not initialised. Call init_db_pool() first.")
    return _pool


async def async_execute_query(query: str, params: Optional[tuple] = None) -> None:
    """Execute a write query (INSERT / UPDATE / DELETE) using the async pool."""
    pool = _get_pool()
    logger.debug("Executing async query", query=query, params=params)
    async with pool.acquire() as conn:
        async with conn.transaction():
            if params is not None:
                await conn.execute(query, *params)
            else:
                await conn.execute(query)
    logger.debug("Async query executed successfully")


async def async_execute_query_with_result(query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """Execute a read query and return all rows as list of dicts."""
    pool = _get_pool()
    logger.debug("Executing async query with result", query=query, params=params)
    async with pool.acquire() as conn:
        if params is not None:
            rows = await conn.fetch(query, *params)
        else:
            rows = await conn.fetch(query)
    logger.debug("Async query executed successfully", result_count=len(rows))
    return [dict(row) for row in rows]


async def async_execute_query_single_result(query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
    """Execute a read query and return the first row as a dict, or None."""
    pool = _get_pool()
    logger.debug("Executing async single-result query", query=query, params=params)
    async with pool.acquire() as conn:
        if params is not None:
            row = await conn.fetchrow(query, *params)
        else:
            row = await conn.fetchrow(query)
    if row is None:
        return None
    return dict(row)


async def async_check_database_connection() -> bool:
    """Lightweight connectivity check using the async pool."""
    try:
        pool = _get_pool()
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error("Async database connection check failed", error=str(e))
        return False


# ---------------------------------------------------------------------------
# Synchronous helpers (psycopg2) – used by background Kafka consumers
# ---------------------------------------------------------------------------

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