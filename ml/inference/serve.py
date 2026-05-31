"""
CloudSentinel — SageMaker Inference Script (script mode)
=========================================================
Loaded by the SageMaker sklearn container via SAGEMAKER_PROGRAM=serve.py.

The four functions below are the SageMaker script-mode contract:
  model_fn   — load artefacts from /opt/ml/model/
  input_fn   — deserialise the HTTP request body
  predict_fn — run inference
  output_fn  — serialise the response

Input (application/json)
------------------------
Single record:
    {"cpu_util": 85.3, "memory_util": 90.1, "latency_ms": 350.0,
     "error_rate": 0.12, "request_count": 42.0}

Batch:
    [{"cpu_util": …}, {"cpu_util": …}]

Output (application/json)
-------------------------
    {
      "predictions": [1, -1, 1],   // 1 = normal, -1 = anomaly
      "scores":      [-0.05, -0.34, -0.02]  // more negative → more anomalous
    }
"""

import json
import logging
import os

import joblib
import numpy as np

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

FEATURES = ["cpu_util", "memory_util", "latency_ms", "error_rate", "request_count"]


# ── SageMaker contract ─────────────────────────────────────────────────────────

def model_fn(model_dir: str) -> dict:
    """Load the IsolationForest and StandardScaler from the model directory."""
    logger.info(f"Loading model artefacts from {model_dir}")
    model  = joblib.load(os.path.join(model_dir, "model.pkl"))
    scaler = joblib.load(os.path.join(model_dir, "scaler.pkl"))
    logger.info("Model artefacts loaded successfully")
    return {"model": model, "scaler": scaler}


def input_fn(request_body: str | bytes, content_type: str = "application/json") -> np.ndarray:
    """
    Parse the incoming request body into a 2-D numpy array.

    Accepts both a single JSON object and a JSON array of objects.
    Missing features default to 0.0.
    """
    if content_type != "application/json":
        raise ValueError(f"Unsupported content type: {content_type!r}. Use application/json.")

    if isinstance(request_body, bytes):
        request_body = request_body.decode("utf-8")

    data = json.loads(request_body)

    # Normalise single-record input to a list
    if isinstance(data, dict):
        data = [data]

    rows = [
        [float(record.get(feature, 0.0)) for feature in FEATURES]
        for record in data
    ]
    return np.array(rows, dtype=np.float64)


def predict_fn(input_data: np.ndarray, model_artifacts: dict) -> dict:
    """
    Scale features and run Isolation Forest.

    Returns a dict with:
      predictions — list of int  (1 = normal, -1 = anomaly)
      scores      — list of float (lower = more anomalous; threshold ≈ –0.1)
    """
    model  = model_artifacts["model"]
    scaler = model_artifacts["scaler"]

    X_scaled    = scaler.transform(input_data)
    predictions = model.predict(X_scaled)       # ndarray of 1 / -1
    scores      = model.score_samples(X_scaled)  # raw anomaly scores

    n_anomalies = int((predictions == -1).sum())
    logger.info(f"Scored {len(predictions)} records — {n_anomalies} anomaly/anomalies flagged")

    return {
        "predictions": predictions.tolist(),
        "scores":      [round(s, 6) for s in scores.tolist()],
    }


def output_fn(prediction: dict, accept: str = "application/json") -> tuple[str, str]:
    """Serialise the prediction dict to JSON."""
    if accept != "application/json":
        raise ValueError(f"Unsupported accept type: {accept!r}. Use application/json.")
    return json.dumps(prediction), "application/json"
