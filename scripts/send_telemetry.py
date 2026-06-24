"""
scripts/send_telemetry.py
─────────────────────────
Sends REAL system metrics (CPU, memory, latency) to the CloudSentinel
/ingest endpoint every N seconds. Requires a valid Cognito JWT.

Usage:
  pip install psutil requests
  python scripts/send_telemetry.py --token <your-jwt-token> [--interval 10] [--anomaly]

Get a token by running:
  python scripts/get_token.py

--anomaly flag sends deliberately spiked values to trigger an alert.
"""
import argparse
import json
import os
import time
import random
import urllib.request
import urllib.error

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

API_ENDPOINT = os.environ.get(
    "CLOUDSENTINEL_API_ENDPOINT",
    "https://<api-id>.execute-api.us-east-1.amazonaws.com/v1/ingest",
)


def real_metrics():
    """Read actual machine metrics via psutil."""
    cpu     = psutil.cpu_percent(interval=1) / 100.0
    mem     = psutil.virtual_memory().percent / 100.0
    latency = random.uniform(30, 200)           # simulated — no real app to measure
    err_rt  = random.uniform(0.0, 0.02)         # simulated
    req_cnt = random.randint(50, 500)
    return dict(cpu_util=cpu, memory_util=mem, latency_ms=round(latency, 1),
                error_rate=round(err_rt, 4), request_count=req_cnt)


def fake_normal_metrics():
    """Realistic-looking normal metrics (no psutil needed)."""
    return dict(
        cpu_util=round(random.uniform(0.10, 0.55), 3),
        memory_util=round(random.uniform(0.30, 0.65), 3),
        latency_ms=round(random.uniform(20, 300), 1),
        error_rate=round(random.uniform(0.0, 0.02), 4),
        request_count=random.randint(100, 600),
    )


def anomaly_metrics():
    """Extreme spike — scores below -0.35 → critical."""
    return dict(
        cpu_util=round(random.uniform(0.92, 1.00), 3),
        memory_util=round(random.uniform(0.90, 1.00), 3),
        latency_ms=round(random.uniform(3000, 8000), 1),
        error_rate=round(random.uniform(0.40, 0.90), 4),
        request_count=random.randint(1, 10),
    )


def mild_anomaly_metrics():
    """Mildly elevated values — scores around -0.10 to -0.30 → medium/high."""
    return dict(
        cpu_util=round(random.uniform(0.70, 0.85), 3),
        memory_util=round(random.uniform(0.75, 0.88), 3),
        latency_ms=round(random.uniform(600, 1200), 1),
        error_rate=round(random.uniform(0.05, 0.15), 4),
        request_count=random.randint(15, 40),
    )


def send(token: str, payload: dict):
    body = json.dumps(payload).encode()
    req  = urllib.request.Request(
        API_ENDPOINT,
        data=body,
        headers={"Authorization": token, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            return res.status, json.loads(res.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token",    required=True, help="Cognito ID token (JWT)")
    parser.add_argument("--interval", type=int, default=10, help="Seconds between sends")
    parser.add_argument("--count",    type=int, default=0,  help="How many to send (0=forever)")
    parser.add_argument("--anomaly",  action="store_true", help="Send extreme spike values (→ critical alerts)")
    parser.add_argument("--mild",     action="store_true", help="Send mildly elevated values (→ medium/high alerts)")
    args = parser.parse_args()

    if args.anomaly:   mode = "ANOMALY (critical)"
    elif args.mild:    mode = "MILD ANOMALY (medium/high)"
    else:              mode = "REAL" if HAS_PSUTIL else "SIMULATED"
    print(f"Mode: {mode} | interval: {args.interval}s | endpoint: {API_ENDPOINT}\n")

    sent = 0
    while args.count == 0 or sent < args.count:
        if args.anomaly:
            metrics = anomaly_metrics()
            tag = "CRITICAL"
        elif args.mild:
            metrics = mild_anomaly_metrics()
            tag = "MILD"
        elif HAS_PSUTIL:
            metrics = real_metrics()
            tag = "real"
        else:
            metrics = fake_normal_metrics()
            tag = "sim"

        status, resp = send(args.token, metrics)
        print(f"[{tag}] cpu={metrics['cpu_util']:.2f} mem={metrics['memory_util']:.2f} "
              f"lat={metrics['latency_ms']}ms err={metrics['error_rate']:.3f} → HTTP {status}")
        sent += 1
        if args.count == 0 or sent < args.count:
            time.sleep(args.interval)


if __name__ == "__main__":
    main()
