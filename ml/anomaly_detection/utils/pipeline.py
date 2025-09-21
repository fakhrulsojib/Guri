import joblib
import numpy as np
from typing import Tuple
import structlog

from ..data.features import LogVolumeFeatureEngineer
from ..models.anomaly_detector import LogVolumeAnomalyDetector

logger = structlog.get_logger()

class LogVolumeAnomalyPipeline:
    def __init__(self, contamination: float = 0.1, random_state: int = 42):
        self.feature_engineer = LogVolumeFeatureEngineer()
        self.anomaly_detector = LogVolumeAnomalyDetector(
            contamination=contamination,
            random_state=random_state
        )
        self.is_fitted = False
    
    def fit(self, df) -> 'LogVolumeAnomalyPipeline':
        X, timestamps = self.feature_engineer.fit_transform(df)
        self.anomaly_detector.fit(X)
        self.is_fitted = True
        logger.info("Pipeline fitted successfully")
        return self
    
    def predict(self, df) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        if not self.is_fitted:
            raise ValueError("Pipeline must be fitted before prediction")
        
        X, timestamps = self.feature_engineer.transform(df)
        predictions = self.anomaly_detector.predict(X)
        scores = self.anomaly_detector.get_anomaly_scores(X)
        
        return predictions, scores, timestamps
    
    def save(self, filepath: str) -> None:
        if not self.is_fitted:
            raise ValueError("Pipeline must be fitted before saving")
        
        pipeline_data = {
            'feature_engineer': self.feature_engineer,
            'anomaly_detector': self.anomaly_detector,
            'is_fitted': self.is_fitted
        }
        
        joblib.dump(pipeline_data, filepath)
        logger.info(f"Pipeline saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str) -> 'LogVolumeAnomalyPipeline':
        pipeline_data = joblib.load(filepath)
        
        pipeline = cls()
        pipeline.feature_engineer = pipeline_data['feature_engineer']
        pipeline.anomaly_detector = pipeline_data['anomaly_detector']
        pipeline.is_fitted = pipeline_data['is_fitted']
        
        logger.info(f"Pipeline loaded from {filepath}")
        return pipeline
