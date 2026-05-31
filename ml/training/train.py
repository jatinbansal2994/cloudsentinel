"""
CloudSentinel — Phase 3: Model Training
========================================
Trains an Isolation Forest on synthetic telemetry data,
packages it (with the inference script) as model.tar.gz,
and uploads to S3 so CDK ml_stack can deploy it.

Usage:
    cd ml/training
    pip install -r requirements.txt
    python train.py --bucket <your-storage-bucket-name>

    # Dry-run (no S3 upload):
    python train.py --bucket dummy --no-upload
"""

import argparse
import json
import os
import shutil
import tarfile

import boto3
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# ── Constants ─────────────────────────────────────────────────────────────────

FEATURES = ["cpu_util", "memory_util", "latency_ms", "error_rate", "request_count"]

ARTIFACT_DIR  = "model_artifacts"
TAR_OUTPUT    = "model.tar.gz"
S3_KEY_PREFIX = "cloudsentinel/models"

# Relative path to the inference script (co-located in ml/)
INFERENCE_SCRIPT = os.path.join(os.path.dirname(__file__), "..", "inference", "serve.py")


# ── Synthetic data ─────────────────────────────────────────────────────────────

def generate_synthetic_data(n_normal: int = 5000, n_anomaly: int = 200) -> pd.DataFrame:
    """
    Simulate per-tenant telemetry.

    Normal behaviour: moderate CPU/memory, low latency, near-zero error rate.
    Anomalies: CPU spikes or drops, memory saturation, high latency, elevated errors.
    """
    rng = np.random.default_rng(42)

    normal = pd.DataFrame({
        "cpu_util":      rng.normal(40,  15, n_normal).clip(0, 100),
        "memory_util":   rng.normal(55,  10, n_normal).clip(0, 100),
        "latency_ms":    rng.normal(120, 40, n_normal).clip(1, None),
        "error_rate":    rng.beta(1, 50, n_normal),
        "request_count": rng.poisson(500, n_normal).astype(float),
    })

    half = n_anomaly // 2
    anomalies = pd.DataFrame({
        # CPU either pegged at 100 % or near-zero (process crash)
        "cpu_util": np.concatenate([
            rng.uniform(90, 100, half),
            rng.uniform(0,   5,  n_anomaly - half),
        ]),
        "memory_util":   rng.uniform(90, 100, n_anomaly),
        "latency_ms":    rng.uniform(1_000, 5_000, n_anomaly),
        "error_rate":    rng.uniform(0.3, 1.0, n_anomaly),
        # Traffic flood or near-silence
        "request_count": np.concatenate([
            rng.uniform(2_000, 5_000, half),
            rng.uniform(0,     5,     n_anomaly - half),
        ]),
    })

    return pd.concat([normal, anomalies], ignore_index=True)


# ── Training ───────────────────────────────────────────────────────────────────

def train(output_dir: str = ARTIFACT_DIR) -> str:
    os.makedirs(output_dir, exist_ok=True)

    print("⟳  Generating synthetic telemetry data …")
    df = generate_synthetic_data()
    print(f"   {len(df):,} samples  ({df[FEATURES].shape[1]} features)")

    print("⟳  Fitting StandardScaler …")
    scaler = StandardScaler()
    X = scaler.fit_transform(df[FEATURES])

    print("⟳  Training IsolationForest …")
    model = IsolationForest(
        n_estimators=200,
        contamination=0.038,          # ≈ 200 / 5200
        max_samples="auto",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X)

    # Quick sanity check on training data
    preds = model.predict(X)
    detected = int((preds == -1).sum())
    print(f"   Anomalies flagged on training set: {detected} / {len(df)}")

    # ── Persist artifacts ──────────────────────────────────────────────────────
    joblib.dump(model,  os.path.join(output_dir, "model.pkl"))
    joblib.dump(scaler, os.path.join(output_dir, "scaler.pkl"))

    metadata = {
        "features":     FEATURES,
        "contamination": 0.038,
        "n_estimators":  200,
        "sklearn_version": __import__("sklearn").__version__,
    }
    with open(os.path.join(output_dir, "metadata.json"), "w") as fh:
        json.dump(metadata, fh, indent=2)

    print(f"✓  Artifacts written to {output_dir}/")
    return output_dir


# ── Packaging ──────────────────────────────────────────────────────────────────

def package_model(artifact_dir: str, output_path: str = TAR_OUTPUT) -> str:
    """
    Build model.tar.gz expected by SageMaker script mode.

    Contents
    --------
    model.pkl       — trained IsolationForest
    scaler.pkl      — fitted StandardScaler
    metadata.json   — feature list + hyper-params
    serve.py        — inference entry-point (SAGEMAKER_PROGRAM)
    """
    # Copy the inference script into the artifact dir
    dest_script = os.path.join(artifact_dir, "serve.py")
    if os.path.exists(INFERENCE_SCRIPT):
        shutil.copy2(INFERENCE_SCRIPT, dest_script)
        print(f"✓  Bundled inference script → {dest_script}")
    else:
        raise FileNotFoundError(
            f"Inference script not found at {INFERENCE_SCRIPT}. "
            "Make sure ml/inference/serve.py exists."
        )

    with tarfile.open(output_path, "w:gz") as tar:
        for fname in os.listdir(artifact_dir):
            tar.add(os.path.join(artifact_dir, fname), arcname=fname)

    size_kb = os.path.getsize(output_path) / 1024
    print(f"✓  Packaged → {output_path}  ({size_kb:.1f} KB)")
    return output_path


# ── Upload ─────────────────────────────────────────────────────────────────────

def upload_to_s3(local_path: str, bucket: str, prefix: str = S3_KEY_PREFIX) -> str:
    s3_key = f"{prefix}/model.tar.gz"
    s3 = boto3.client("s3")
    print(f"⟳  Uploading to s3://{bucket}/{s3_key} …")
    s3.upload_file(local_path, bucket, s3_key)
    s3_uri = f"s3://{bucket}/{s3_key}"
    print(f"✓  Uploaded: {s3_uri}")
    return s3_uri


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train CloudSentinel anomaly model")
    parser.add_argument(
        "--bucket", required=True,
        help="S3 bucket name output by storage_stack (CloudSentinelDataBucket)"
    )
    parser.add_argument(
        "--no-upload", action="store_true",
        help="Skip S3 upload — useful for local testing"
    )
    parser.add_argument(
        "--artifact-dir", default=ARTIFACT_DIR,
        help=f"Local directory for model artifacts (default: {ARTIFACT_DIR})"
    )
    args = parser.parse_args()

    artifact_dir = train(args.artifact_dir)
    tar_path     = package_model(artifact_dir)

    if args.no_upload:
        print(f"\n📦  Dry-run complete. Artifacts at: {tar_path}")
    else:
        s3_uri = upload_to_s3(tar_path, args.bucket)
        print(f"""
╔══════════════════════════════════════════════════════╗
║  Model uploaded successfully                         ║
║  S3 URI : {s3_uri:<41}║
║                                                      ║
║  Next step:                                          ║
║    cdk deploy CloudSentinelMlStack                   ║
╚══════════════════════════════════════════════════════╝
""")
