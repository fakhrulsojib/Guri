#!/usr/bin/env python3
import os
import sys
import argparse
import structlog
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from ml.anomaly_detection.data import LogVolumeDataLoader
from ml.anomaly_detection.utils import LogVolumeAnomalyPipeline

logger = structlog.get_logger()

def main():
    parser = argparse.ArgumentParser(description='Train log volume anomaly detection model')
    parser.add_argument('--data-limit', type=int, help='Limit number of records to load for training')
    parser.add_argument('--contamination', type=float, default=0.1, help='Expected proportion of anomalies')
    parser.add_argument('--output-path', type=str, default='ml/anomaly_detection/models/pipeline.joblib', 
                       help='Path to save the trained pipeline')
    parser.add_argument('--random-state', type=int, default=42, help='Random state for reproducibility')
    
    args = parser.parse_args()
    
    try:
        logger.info("Starting anomaly detection model training")
        
        data_loader = LogVolumeDataLoader()
        df = data_loader.load_data(limit=args.data_limit)
        
        if df.empty:
            logger.error("No data loaded from database")
            return 1
        
        logger.info(f"Loaded {len(df)} records for training")
        
        pipeline = LogVolumeAnomalyPipeline(
            contamination=args.contamination,
            random_state=args.random_state
        )
        
        pipeline.fit(df)
        
        os.makedirs(os.path.dirname(args.output_path), exist_ok=True)
        pipeline.save(args.output_path)
        
        logger.info(f"Training completed. Pipeline saved to {args.output_path}")
        
        predictions, scores, timestamps = pipeline.predict(df)
        anomaly_count = sum(predictions)
        
        logger.info(f"Model performance: {anomaly_count} anomalies detected out of {len(df)} records ({anomaly_count/len(df)*100:.2f}%)")
        
        return 0
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
