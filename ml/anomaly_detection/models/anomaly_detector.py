import numpy as np
from pyod.models.iforest import IForest
from typing import Tuple
import structlog

logger = structlog.get_logger()

class LogVolumeAnomalyDetector:
    def __init__(self, contamination: float = 0.1, random_state: int = 42):
        self.model = IForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100
        )
        self.is_fitted = False
    
    def fit(self, X: np.ndarray) -> 'LogVolumeAnomalyDetector':
        self.model.fit(X)
        self.is_fitted = True
        logger.info(f"Anomaly detector fitted on {X.shape[0]} samples")
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        return self.model.predict(X)
    
    def decision_function(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model must be fitted before decision function")
        
        return self.model.decision_function(X)
    
    def get_anomaly_scores(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model must be fitted before getting anomaly scores")
        
        return -self.model.decision_function(X)
