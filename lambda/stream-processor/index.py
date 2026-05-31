"""
stream-processor/index.py
─────────────────────────
Triggered by Kinesis Data Stream.
For each batch of telemetry events:
  1. Decodes the base64 Kinesis payload
  2. Calls SageMaker Isolation Forest endpoint
  3. If anomaly detected, writes an alert to DynamoDB and publishes to SNS

SageMaker response format (from ml/inference/serve.py):
  {"predictions": [1 or -1], "scores": [-0.34]}
   predictions: 1 = normal, -1 = anomaly
   scores:      more negative = more anomalous (threshold ≈ -0.10)
"""
import json
import os
import base64
import uuid
import boto3
from datetime import datetime, timezone
from decimal import Decimal

dynamodb   = boto3.resource('dynamodb')
sagemaker  = boto3.client('sagemaker-runtime')
sns_client = boto3.client('sns')

ALERT_TABLE        = os.environ['ALERT_TABLE']
SAGEMAKER_ENDPOINT = os.environ['SAGEMAKER_ENDPOINT']
ALERT_TOPIC_ARN    = os.environ.get('ALERT_TOPIC_ARN', '')

# Score below this is stored even if prediction == 1 (catches borderline cases)
# Isolation Forest scores are negative — more negative = more anomalous
SCORE_THRESHOLD = float(os.environ.get('ANOMALY_THRESHOLD', '-0.10'))

alert_table = dynamodb.Table(ALERT_TABLE)

# Features the model expects — must match ml/training/train.py
FEATURES = ['cpu_util', 'memory_util', 'latency_ms', 'error_rate', 'request_count']


def handler(event, context):
    records = event.get('Records', [])
    print(f"Processing {len(records)} Kinesis records")

    alerts_written = 0
    for record in records:
        # Kinesis payloads are base64-encoded
        raw     = base64.b64decode(record['kinesis']['data']).decode('utf-8')
        payload = json.loads(raw)

        tenant_id = payload.get('tenantId')
        if not tenant_id:
            print("Skipping — missing tenantId")
            continue

        prediction, score = invoke_sagemaker(payload)
        print(f"tenant={tenant_id} prediction={prediction} score={score:.4f}")

        # Flag if model says anomaly (-1) OR score is below threshold
        is_anomaly = (prediction == -1) or (score < SCORE_THRESHOLD)
        if is_anomaly:
            alert_id = write_alert(tenant_id, payload, prediction, score)
            publish_sns(tenant_id, alert_id, payload, score)
            alerts_written += 1

    return {
        'statusCode': 200,
        'processed':  len(records),
        'alerts':     alerts_written,
    }


def invoke_sagemaker(payload: dict) -> tuple[int, float]:
    """
    Send telemetry to SageMaker endpoint.

    Returns
    -------
    prediction : int    1 = normal, -1 = anomaly
    score      : float  more negative = more anomalous
    """
    # Extract only the features the model was trained on
    # Missing fields default to 0.0
    features = {f: float(payload.get(f, 0.0)) for f in FEATURES}

    try:
        response = sagemaker.invoke_endpoint(
            EndpointName=SAGEMAKER_ENDPOINT,
            ContentType='application/json',
            Accept='application/json',
            Body=json.dumps(features).encode('utf-8'),
        )
        result     = json.loads(response['Body'].read())
        prediction = int(result['predictions'][0])    # 1 or -1
        score      = float(result['scores'][0])       # e.g. -0.34
        return prediction, score

    except Exception as e:
        # Never let ML failures break the pipeline
        print(f"SageMaker error (non-fatal): {e}")
        return 1, 0.0   # treat as normal on failure


def severity(score: float) -> str:
    """Map an Isolation Forest score to a severity label."""
    if score < -0.35:  return 'critical'
    if score < -0.25:  return 'high'
    if score < -0.10:  return 'medium'
    return 'low'


def write_alert(tenant_id: str, payload: dict, prediction: int, score: float) -> str:
    """Persist a confirmed anomaly alert to DynamoDB. Returns the new alertId."""
    now      = datetime.now(timezone.utc)
    alert_id = str(uuid.uuid4())

    alert_table.put_item(Item={
        'tenantId':   tenant_id,
        'alertId':    alert_id,
        'severity':   severity(score),
        'score':      Decimal(str(round(score, 6))),
        'prediction': prediction,
        # Raw feature snapshot at time of alert
        'features': {
            f: Decimal(str(round(float(payload.get(f, 0.0)), 4)))
            for f in FEATURES
        },
        'source':    payload.get('source', 'unknown'),
        'createdAt': now.isoformat(),
        # TTL: auto-delete alerts after 7 days
        'ttl': int(now.timestamp()) + (7 * 86_400),
    })
    print(f"Alert written: tenant={tenant_id} severity={severity(score)} score={score:.4f}")
    return alert_id


def publish_sns(tenant_id: str, alert_id: str, payload: dict, score: float):
    """Publish an anomaly notification to SNS. No-op if ALERT_TOPIC_ARN is unset."""
    if not ALERT_TOPIC_ARN:
        return
    try:
        sev = severity(score)
        message = {
            'tenantId': tenant_id,
            'alertId':  alert_id,
            'severity': sev,
            'score':    round(score, 4),
            'source':   payload.get('source', 'unknown'),
        }
        sns_client.publish(
            TopicArn=ALERT_TOPIC_ARN,
            Subject=f"CloudSentinel: {sev.upper()} anomaly detected for tenant {tenant_id}",
            Message=json.dumps(message),
            MessageAttributes={
                'tenantId': {'DataType': 'String', 'StringValue': tenant_id},
                'severity': {'DataType': 'String', 'StringValue': sev},
            },
        )
    except Exception as e:
        # Never let notification failures break the pipeline
        print(f"SNS publish error (non-fatal): {e}")
