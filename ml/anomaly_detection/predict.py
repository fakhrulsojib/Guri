#!/usr/bin/env python3
import os
import sys
import argparse
import pandas as pd
import structlog
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from ml.anomaly_detection.data import LogVolumeDataLoader
from ml.anomaly_detection.utils import LogVolumeAnomalyPipeline

logger = structlog.get_logger()

def main():
    parser = argparse.ArgumentParser(description='Predict anomalies using trained model')
    parser.add_argument('--model-path', type=str, default='ml/anomaly_detection/models/pipeline.joblib',
                       help='Path to the trained pipeline')
    parser.add_argument('--data-limit', type=int, help='Limit number of records to predict on')
    parser.add_argument('--output-csv', type=str, help='Path to save predictions as CSV')
    
    args = parser.parse_args()
    
    try:
        logger.info("Loading trained pipeline")
        pipeline = LogVolumeAnomalyPipeline.load(args.model_path)
        
        logger.info("Loading data for prediction")
        data_loader = LogVolumeDataLoader()
        df = data_loader.load_data(limit=args.data_limit, order='ASC')
        
        if df.empty:
            logger.error("No data loaded from database")
            return 1
        
        logger.info(f"Predicting on {len(df)} records")
        predictions, scores, timestamps = pipeline.predict(df)
        
        results_df = pd.DataFrame({
            'timestamp': timestamps,
            'source_id': df['source_id'].values,
            'log_count': df['log_count'].values,
            'is_anomaly': predictions,
            'anomaly_score': scores
        })
        
        if args.output_csv:
            results_df.to_csv(args.output_csv, index=False)
            logger.info(f"Predictions saved to {args.output_csv}")
        
        anomaly_count = sum(predictions)
        logger.info(f"Found {anomaly_count} anomalies out of {len(df)} records")
        
        if anomaly_count > 0:
            anomaly_df = results_df[results_df['is_anomaly'] == 1]
            logger.info("Top anomalies by score:")
            for _, row in anomaly_df.nlargest(5, 'anomaly_score').iterrows():
                logger.info(f"  {row['timestamp']} | Source {row['source_id']} | Count {row['log_count']} | Score {row['anomaly_score']:.3f}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
