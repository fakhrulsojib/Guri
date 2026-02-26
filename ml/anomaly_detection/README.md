# 📈 Log Volume Anomaly Detection
> **Goal:** Provide unsupervised anomaly detection for log volume data using `IsolationForest` from PyOD.

## ✨ Features
- **Data Loading**: Fetches data from `log_volume_minute` PostgreSQL table.
- **Feature Engineering**: 
  - One-hot encoding for `source_id` (categorical).
  - Time features: `minute_of_day` (0-1439), `day_of_week` (0-6).
  - Standard scaling for numeric features.
- **Anomaly Detection**: `IsolationForest` model with configurable contamination.
- **Pipeline**: Complete preprocessing and modeling pipeline saved as a single `.joblib` file.

## 🚀 Usage

### 🏋️ Training
```bash
# Train with default settings
python ml/anomaly_detection/train.py

# Train with custom parameters
python ml/anomaly_detection/train.py --data-limit 10000 --contamination 0.05 --output-path ml/anomaly_detection/models/custom_pipeline.joblib
```

### 🔮 Prediction
```bash
# Predict on recent data
python ml/anomaly_detection/predict.py

# Save predictions to CSV
python ml/anomaly_detection/predict.py --model-path ml/anomaly_detection/models/pipeline.joblib --output-csv predictions.csv
```

## 📐 Model Architecture
1. **DataLoader**: Connects to PostgreSQL and loads log volume data.
2. **FeatureEngineer**: Extracts time features, one-hot encodes categoricals, standardizes numericals.
3. **AnomalyDetector**: `IsolationForest` model for unsupervised anomaly detection.
4. **Pipeline**: Combines all components with fit/predict/save/load methods.

## ⚙️ Dependencies
| Dependency | Purpose |
|---|---|
| `pandas` / `numpy` | Data manipulation and numeric operations. |
| `scikit-learn` | Pipeline standards and preprocessing metrics. |
| `pyod` | Implementation of `IsolationForest` and outlier detection. |
| `joblib` | Model persistence and saving. |
| `psycopg2-binary` | PostgreSQL connection adapter. |

## 🚫 Constraints (AI Rules)
- Do NOT modify the prediction and training parameter signatures without updating automated scripts.
- Do NOT assume live streaming data during the training phase. The model trains on batched SQL pull datasets from `log_volume_minute`.
- Do NOT save partial pipelines. Always utilize `joblib` for the full FeatureEngineer + AnomalyDetector bundled pipeline object.
