import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple
import structlog

# Add the project root to Python path to import ML modules
sys.path.append('/app')

from ml.anomaly_detection.utils import LogVolumeAnomalyPipeline
from database.database import execute_query

logger = structlog.get_logger()

class AnomalyDetectionService:
    def __init__(self, model_path: str = "/app/ml/anomaly_detection/models/pipeline.joblib"):
        self.model_path = model_path
        self.pipeline: Optional[LogVolumeAnomalyPipeline] = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the trained anomaly detection pipeline"""
        try:
            if os.path.exists(self.model_path):
                self.pipeline = LogVolumeAnomalyPipeline.load(self.model_path)
                logger.info("Anomaly detection model loaded successfully", model_path=self.model_path)
            else:
                logger.warning("Anomaly detection model not found", model_path=self.model_path)
                self.pipeline = None
        except Exception as e:
            logger.error("Failed to load anomaly detection model", error=str(e))
            self.pipeline = None
    
    def _get_recent_log_volume_data(self, minutes: int = 30) -> pd.DataFrame:
        """Fetch recent log volume data from database"""
        query = """
        SELECT 
            source_id,
            bucket_minute,
            log_count
        FROM log_volume_minute
        WHERE bucket_minute >= %s
        ORDER BY bucket_minute DESC
        """
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        
        try:
            from database.database import get_connection
            with get_connection() as conn:
                df = pd.read_sql_query(query, conn, params=(cutoff_time,))
                logger.info(f"Fetched {len(df)} log volume records from last {minutes} minutes")
                return df
        except Exception as e:
            logger.error("Failed to fetch log volume data", error=str(e))
            return pd.DataFrame()
    
    def detect_anomalies(self, minutes: int = 30) -> List[Dict[str, Any]]:
        """Detect anomalies in recent log volume data"""
        if not self.pipeline:
            logger.warning("Anomaly detection model not available")
            return []
        
        try:
            # Fetch recent data
            df = self._get_recent_log_volume_data(minutes)
            
            if df.empty:
                logger.info("No data available for anomaly detection")
                return []
            
            # Run anomaly detection
            predictions, scores, timestamps = self.pipeline.predict(df)
            
            # Create anomaly results
            anomalies = []
            for i, (prediction, score, timestamp) in enumerate(zip(predictions, scores, timestamps)):
                if prediction == 1:  # Anomaly detected
                    anomaly = {
                        'source_id': df.iloc[i]['source_id'],
                        'timestamp': timestamp,
                        'log_count': df.iloc[i]['log_count'],
                        'anomaly_score': float(score),
                        'detected_at': datetime.now(timezone.utc).isoformat()
                    }
                    anomalies.append(anomaly)
            
            logger.info(f"Detected {len(anomalies)} anomalies in last {minutes} minutes")
            return anomalies
            
        except Exception as e:
            logger.error("Failed to detect anomalies", error=str(e))
            return []
    
    def get_anomaly_summary(self, minutes: int = 30) -> Dict[str, Any]:
        """Get summary of anomalies detected"""
        anomalies = self.detect_anomalies(minutes)
        
        if not anomalies:
            return {
                'total_anomalies': 0,
                'anomalies_by_source': {},
                'top_anomalies': [],
                'detection_time': datetime.now(timezone.utc).isoformat()
            }
        
        # Group by source_id
        anomalies_by_source = {}
        for anomaly in anomalies:
            source_id = anomaly['source_id']
            if source_id not in anomalies_by_source:
                anomalies_by_source[source_id] = 0
            anomalies_by_source[source_id] += 1
        
        # Get top 5 anomalies by score
        top_anomalies = sorted(anomalies, key=lambda x: x['anomaly_score'], reverse=True)[:5]
        
        return {
            'total_anomalies': len(anomalies),
            'anomalies_by_source': anomalies_by_source,
            'top_anomalies': top_anomalies,
            'detection_time': datetime.now(timezone.utc).isoformat()
        }
    
    def is_model_available(self) -> bool:
        """Check if the anomaly detection model is available"""
        return self.pipeline is not None

# Global instance
anomaly_detection_service = AnomalyDetectionService()
