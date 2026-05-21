"""
ml/training/train.py
────────────────────
Trains an Isolation Forest model on telemetry data.

Run locally first to verify everything works:
  python ml/training/train.py

Then run as a SageMaker training job (see scripts/run_training_job.py).

The trained model is saved to ml/training/model/ as three files:
  model.pkl    — the trained IsolationForest
  scaler.pkl   — the StandardScaler fitted on training data
  features.json — the feature names in the correct order
"""
import argparse
import json
import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report

FEATURES = [
    'response_time_ms',   # API response time
    'error_rate',         # fraction of requests returning 5xx
    'requests_per_sec',   # throughput
    'cpu_percent',        # server CPU usage
    'memory_percent',     # server memory usage
]


def generate_synthetic_data(n_samples: int = 10_000) -> pd.DataFrame:
    """
    Generate realistic synthetic telemetry with ~2% injected anomalies.
    Use this until you have real tenant data to train on.
    """
    np.random.seed(42)
    df = pd.DataFrame({
        'response_time_ms': np.random.normal(200, 40,  n_samples).clip(10),
        'error_rate':        np.random.normal(0.01, 0.005, n_samples).clip(0, 1),
        'requests_per_sec':  np.random.normal(100, 20,  n_samples).clip(0),
        'cpu_percent':       np.random.normal(40,  10,  n_samples).clip(0, 100),
        'memory_percent':    np.random.normal(60,  8,   n_samples).clip(0, 100),
    })

    # Inject anomalies: 2% of rows get extreme values
    anomaly_idx = np.random.choice(n_samples, size=int(n_samples * 0.02), replace=False)
    df.loc[anomaly_idx, 'response_time_ms'] *= np.random.uniform(4, 10, len(anomaly_idx))
    df.loc[anomaly_idx, 'error_rate']        = np.random.uniform(0.3, 1.0, len(anomaly_idx))
    df.loc[anomaly_idx, 'cpu_percent']       = np.random.uniform(90, 100, len(anomaly_idx))
    df['label'] = 0
    df.loc[anomaly_idx, 'label'] = 1

    print(f"Generated {n_samples} samples ({len(anomaly_idx)} anomalies = {len(anomaly_idx)/n_samples:.1%})")
    return df


def train(data_path: str = None, output_path: str = 'model/'):
    print("=" * 50)
    print("CloudSentinel — Anomaly Detection Training")
    print("=" * 50)

    # Load or generate data
    if data_path and os.path.exists(data_path):
        print(f"Loading data from {data_path}")
        df = pd.read_csv(data_path)
    else:
        print("No data file provided — using synthetic data")
        df = generate_synthetic_data()

    X = df[FEATURES].fillna(0)
    y = df.get('label', pd.Series([0] * len(df)))  # for evaluation only

    # Scale features — Isolation Forest is sensitive to feature scale
    print("Fitting StandardScaler...")
    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train Isolation Forest
    print("Training Isolation Forest (n_estimators=200)...")
    model = IsolationForest(
        n_estimators=200,
        contamination=0.02,   # expected fraction of anomalies in training data
        max_samples='auto',
        random_state=42,
        n_jobs=-1,            # use all CPU cores
    )
    model.fit(X_scaled)

    # Evaluate on training data (rough sanity check)
    preds = model.predict(X_scaled)
    preds_binary = (preds == -1).astype(int)  # IF: -1=anomaly, 1=normal
    print("\nTraining set evaluation:")
    print(classification_report(y, preds_binary, target_names=['normal', 'anomaly'], zero_division=0))

    # Save artifacts
    os.makedirs(output_path, exist_ok=True)
    with open(f'{output_path}/model.pkl',    'wb') as f: pickle.dump(model,  f)
    with open(f'{output_path}/scaler.pkl',   'wb') as f: pickle.dump(scaler, f)
    with open(f'{output_path}/features.json', 'w') as f: json.dump({'features': FEATURES}, f)
    print(f"\nModel artifacts saved to {output_path}/")
    print("  model.pkl  scaler.pkl  features.json")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train CloudSentinel anomaly detector')
    parser.add_argument('--data-path',   default=None,    help='Path to CSV training data')
    parser.add_argument('--output-path', default='model/', help='Where to save model artifacts')
    args = parser.parse_args()
    train(args.data_path, args.output_path)
