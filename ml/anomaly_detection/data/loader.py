import os
import psycopg2
import pandas as pd
from typing import Optional
import structlog

logger = structlog.get_logger()

class LogVolumeDataLoader:
    def __init__(self):
        self.host = os.environ.get("POSTGRES_HOST", "db")
        self.dbname = os.environ.get("POSTGRES_DB", "postgres")
        self.user = os.environ.get("POSTGRES_USER", "postgres")
        self.password = os.environ.get("POSTGRES_PASSWORD", "password69")
    
    def _get_connection(self):
        return psycopg2.connect(
            host=self.host,
            dbname=self.dbname,
            user=self.user,
            password=self.password
        )
    
    def load_data(self, limit: Optional[int] = None, order: str = 'DESC') -> pd.DataFrame:
        query = f"""
        SELECT 
            source_id,
            bucket_minute,
            log_count
        FROM log_volume_minute
        ORDER BY bucket_minute {order}
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        try:
            with self._get_connection() as conn:
                df = pd.read_sql_query(query, conn)
                logger.info(f"Loaded {len(df)} records from log_volume_minute in {order} order")
                return df
        except Exception as e:
            logger.error(f"Failed to load data: {str(e)}")
            raise
