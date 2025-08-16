import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
from datetime import datetime

PG_HOST = os.environ.get("POSTGRES_HOST", "db")
PG_DB = os.environ.get("POSTGRES_DB", "postgres")
PG_USER = os.environ.get("POSTGRES_USER", "postgres")
PG_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "password69")

def get_connection():
    return psycopg2.connect(
        host=PG_HOST,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD
    )

def execute_query(query: str, params: Optional[tuple] = None) -> None:
    print(f"[DB] Executing query: {query}")
    if params:
        print(f"[DB] With params: {params}")
    
    conn = get_connection()
    cur = conn.cursor()
    try:
        if params is not None:
            if query.count('%s') != len(params):
                print(f"[DB][ERROR] Parameter count mismatch: {len(params)} params for {query.count('%s')} placeholders")
                raise ValueError(f"Parameter count ({len(params)}) does not match placeholders ({query.count('%s')})")
            cur.execute(query, params)
        else:
            cur.execute(query)
        conn.commit()
        print(f"[DB] Query executed successfully.")
    except Exception as e:
        print(f"[DB][ERROR] Error executing query: {query} with params: {params} - {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def execute_query_with_result(query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    print(f"[DB] Executing query: {query}")
    if params:
        print(f"[DB] With params: {params}")
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        if params is not None:
            if query.count('%s') != len(params):
                print(f"[DB][ERROR] Parameter count mismatch: {len(params)} params for {query.count('%s')} placeholders")
                raise ValueError(f"Parameter count ({len(params)}) does not match placeholders ({query.count('%s')})")
            cur.execute(query, params)
        else:
            cur.execute(query)
        
        conn.commit()
        
        results = cur.fetchall()
        print(f"[DB] Query executed successfully. Found {len(results)} results.")
        return [dict(row) for row in results]
    except Exception as e:
        print(f"[DB][ERROR] Error executing query: {query} with params: {params} - {e}")
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
        print(f"Database connection failed: {e}")
        return False 