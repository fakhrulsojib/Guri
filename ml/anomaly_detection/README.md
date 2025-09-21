# Log Volume Anomaly Detection

This module provides unsupervised anomaly detection for log volume data using IsolationForest from PyOD.

## Features

- **Data Loading**: Fetches data from `log_volume_minute` PostgreSQL table
- **Feature Engineering**: 
  - One-hot encoding for `source_id` (categorical)
  - Time features: `minute_of_day` (0-1439), `day_of_week` (0-6)
  - Standard scaling for numeric features
- **Anomaly Detection**: IsolationForest model with configurable contamination
- **Pipeline**: Complete preprocessing and modeling pipeline saved as single joblib file

## Usage

### Training

```bash
# Train with default settings
python ml/anomaly_detection/train.py

# Train with custom parameters
python ml/anomaly_detection/train.py \
    --data-limit 10000 \
    --contamination 0.05 \
    --output-path ml/anomaly_detection/models/custom_pipeline.joblib

# Sample
docker compose exec backend python ml/anomaly_detection/train.py --data-limit 5000 --contamination 0.003
```

### Prediction

```bash
# Predict on recent data
python ml/anomaly_detection/predict.py

# Save predictions to CSV
python ml/anomaly_detection/predict.py \
    --model-path ml/anomaly_detection/models/pipeline.joblib \
    --output-csv predictions.csv
```

### Programmatic Usage

```python
from ml.anomaly_detection import LogVolumeAnomalyPipeline, LogVolumeDataLoader

# Load data
loader = LogVolumeDataLoader()
df = loader.load_data(limit=1000)

# Train pipeline
pipeline = LogVolumeAnomalyPipeline(contamination=0.1)
pipeline.fit(df)
pipeline.save('pipeline.joblib')

# Load and predict
pipeline = LogVolumeAnomalyPipeline.load('pipeline.joblib')
predictions, scores, timestamps = pipeline.predict(df)
```

## Model Architecture

1. **DataLoader**: Connects to PostgreSQL and loads log volume data
2. **FeatureEngineer**: 
   - Extracts time features from timestamps
   - One-hot encodes categorical variables
   - Standardizes numeric features
3. **AnomalyDetector**: IsolationForest model for unsupervised anomaly detection
4. **Pipeline**: Combines all components with fit/predict/save/load methods

## Dependencies

- pandas
- numpy
- scikit-learn
- pyod
- joblib
- psycopg2-binary
