import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from typing import Tuple
import structlog

logger = structlog.get_logger()

class LogVolumeFeatureEngineer:
    def __init__(self):
        self.one_hot_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        self.scaler = StandardScaler()
        self.is_fitted = False
    
    def _extract_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['bucket_minute'] = pd.to_datetime(df['bucket_minute'])
        
        df['minute_of_day'] = df['bucket_minute'].dt.hour * 60 + df['bucket_minute'].dt.minute
        df['day_of_week'] = df['bucket_minute'].dt.dayofweek
        
        return df
    
    def fit_transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        df_processed = self._extract_time_features(df)
        
        source_id_encoded = self.one_hot_encoder.fit_transform(df_processed[['source_id']])
        
        numeric_features = df_processed[['minute_of_day', 'day_of_week', 'log_count']].values
        numeric_features_scaled = self.scaler.fit_transform(numeric_features)
        
        features = np.hstack([source_id_encoded, numeric_features_scaled])
        
        self.is_fitted = True
        logger.info(f"Feature engineering completed. Shape: {features.shape}")
        
        return features, df_processed['bucket_minute'].values
    
    def transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        if not self.is_fitted:
            raise ValueError("Feature engineer must be fitted before transform")
        
        df_processed = self._extract_time_features(df)
        
        source_id_encoded = self.one_hot_encoder.transform(df_processed[['source_id']])
        
        numeric_features = df_processed[['minute_of_day', 'day_of_week', 'log_count']].values
        numeric_features_scaled = self.scaler.transform(numeric_features)
        
        features = np.hstack([source_id_encoded, numeric_features_scaled])
        
        return features, df_processed['bucket_minute'].values
