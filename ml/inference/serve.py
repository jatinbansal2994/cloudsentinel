"""
ml/inference/serve.py
─────────────────────
Flask server that SageMaker wraps as a real-time inference endpoint.

SageMaker requires exactly two routes:
  GET  /ping         → return 200 (health check, called every 30s)
  POST /invocations  → accept JSON metric, return anomaly score

Input  (JSON): { "response_time_ms": 850, "error_rate": 0.4, ... }
Output (JSON): { "score": 0.87, "threshold": 0.7, "is_anomaly": true }
"""
import json
import os
import pickle
import numpy as np
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load model once at container startup (not per-request)
MODEL_DIR = os.environ.get('MODEL_DIR', 'model/')

with open(f'{MODEL_DIR}/model.pkl',    'rb') as f: model  = pickle.load(f)
with open(f'{MODEL_DIR}/scaler.pkl',   'rb') as f: scaler = pickle.load(f)
with open(f'{MODEL_DIR}/features.json') as f:
    FEATURES  = json.load(f)['features']

THRESHOLD = 0.7


@app.get('/ping')
def ping():
    """SageMaker health check. Must return 200."""
    return 'OK', 200


@app.post('/invocations')
def predict():
    """
    Score a single telemetry event for anomalies.
    Returns a score between 0 (normal) and 1 (definite anomaly).
    """
    payload = request.get_json(force=True)

    # Build feature vector in the exact order the model was trained on
    row = [float(payload.get(f, 0.0)) for f in FEATURES]
    X   = scaler.transform([row])

    # Isolation Forest decision_function: negative = more anomalous
    # We map it to 0-1 where 1 = most anomalous
    raw_score = model.decision_function(X)[0]
    score     = float(np.clip(1.0 - (raw_score + 0.5), 0.0, 1.0))

    return jsonify({
        'score':      round(score, 4),
        'threshold':  THRESHOLD,
        'is_anomaly': score >= THRESHOLD,
        'features':   dict(zip(FEATURES, row)),
    })


if __name__ == '__main__':
    # Local testing: python serve.py
    app.run(host='0.0.0.0', port=8080, debug=True)
