# Sending Telemetry to CloudSentinel

This guide explains how to stream metrics from your own machine into the CloudSentinel pipeline so you can see real anomaly detection working end-to-end.

---

## How it works

```
Your machine
     │  (CPU, memory, latency, error rate, request count)
     ▼
POST /ingest  →  API Gateway  →  Lambda  →  Kinesis
                                                │
                                                ▼
                                    stream-processor Lambda
                                                │
                                         SageMaker scores it
                                                │
                                    ┌───────────┴──────────┐
                                  normal               anomaly
                                (ignored)          → DynamoDB alert
                                                   → SNS email
                                                   → Alerts page
```

---

## Step 1 — Install dependencies

```bash
pip install psutil          # reads real CPU and memory from your machine
```

`psutil` is optional. Without it the script sends realistic simulated values instead of real readings.

---

## Step 2 — Get an auth token

Every API call requires a Cognito JWT. Run the helper script to fetch one:

```bash
source .venv/bin/activate
python scripts/get_token.py
```

Copy the long token string it prints. Tokens expire after **1 hour** — run the script again if you get `401` errors.

---

## Step 3 — Send telemetry

### Real machine metrics (recommended)

Reads your actual CPU and memory every 10 seconds and sends them to the pipeline:

```bash
python scripts/send_telemetry.py --token "<paste-token-here>" --interval 10
```

Example output:
```
Mode: REAL | interval: 10s
[real] cpu=0.14 mem=0.52 lat=87.3ms err=0.008 → HTTP 202
[real] cpu=0.09 mem=0.53 lat=112.1ms err=0.003 → HTTP 202
```

Your machine's normal CPU (< 60%) and memory levels won't trigger alerts — the Isolation Forest model was trained to recognise typical usage as normal.

---

### Trigger a critical alert

In a second terminal, send extreme spike values:

```bash
python scripts/send_telemetry.py --token "<paste-token-here>" --anomaly --count 3
```

Example output:
```
Mode: ANOMALY (critical)
[CRITICAL] cpu=0.99 mem=0.97 lat=5200.1ms err=0.762 → HTTP 202
[CRITICAL] cpu=0.95 mem=0.98 lat=4800.4ms err=0.583 → HTTP 202
[CRITICAL] cpu=0.98 mem=0.93 lat=6100.7ms err=0.820 → HTTP 202
```

---

### Trigger medium / high alerts

Send mildly elevated values that sit between normal and extreme:

```bash
python scripts/send_telemetry.py --token "<paste-token-here>" --mild --count 5
```

Example output:
```
Mode: MILD ANOMALY (medium/high)
[MILD] cpu=0.78 mem=0.83 lat=940.2ms err=0.112 → HTTP 202
```

---

### Run continuously

Omit `--count` to stream forever (Ctrl+C to stop):

```bash
python scripts/send_telemetry.py --token "<paste-token-here>" --interval 15
```

---

## Step 4 — View alerts on the dashboard

1. Open the CloudFront URL in your browser
2. Go to the **Alerts** page
3. Wait ~30 seconds after sending anomalous events
4. Refresh — new alerts appear with severity, score, and timestamp

---

## What the 5 features mean

| Feature | What it measures | Normal range |
|---------|-----------------|--------------|
| `cpu_util` | CPU usage (0.0 – 1.0) | 0.05 – 0.60 |
| `memory_util` | RAM usage (0.0 – 1.0) | 0.30 – 0.70 |
| `latency_ms` | API response time in ms | 20 – 400 |
| `error_rate` | Fraction of requests that failed | 0.00 – 0.03 |
| `request_count` | Requests per interval | 50 – 600 |

The Isolation Forest was trained on synthetic data in those ranges. Values outside them push the anomaly score negative and trigger alerts.

---

## Sending custom JSON via the dashboard

You can also send one-off events from the **Ingest** page in the dashboard without running any scripts. Edit the JSON payload and click **Send Event**:

```json
{
  "cpu_util": 0.95,
  "memory_util": 0.90,
  "latency_ms": 4500,
  "error_rate": 0.60,
  "request_count": 5
}
```

---

## Sending from a real server or application

Any service that can make an HTTP POST can send telemetry. Include your Cognito ID token as the `Authorization` header:

```bash
curl -X POST https://<api-id>.execute-api.us-east-1.amazonaws.com/v1/ingest \
  -H "Authorization: <id-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "cpu_util": 0.45,
    "memory_util": 0.60,
    "latency_ms": 130,
    "error_rate": 0.01,
    "request_count": 320
  }'
```

The `tenantId` is read from the JWT automatically — you do not need to include it in the payload.

---

## Severity reference

| Score (decision_function) | Severity |
|---------------------------|----------|
| ≥ 0.03 | Normal — no alert stored |
| 0.00 – 0.03 | Medium |
| -0.04 – -0.01 | High |
| < -0.04 | Critical |
