"""
stream-processor/index.py
────────────────────────
Triggered by Kinesis Data Stream.
For each batch of telemetry events:
  1. Decodes the base64 Kinesis payload
  2. Calls SageMaker to get an anomaly score (0.0 – 1.0)
  3. If score >= threshold, writes an alert to DynamoDB
"""
import json
import os
import base64
import uuid
import boto3
from datetime import datetime, timezone

dynamodb  = boto3.resource('dynamodb')
sagemaker = boto3.client('sagemaker-runtime')

ALERT_TABLE        = os.environ['ALERT_TABLE']
SAGEMAKER_ENDPOINT = os.environ['SAGEMAKER_ENDPOINT']
ANOMALY_THRESHOLD  = float(os.environ.get('ANOMALY_THRESHOLD', '0.7'))

alert_table = dynamodb.Table(ALERT_TABLE)


def handler(event, context):
    records = event.get('Records', [])
    print(f"Processing {len(records)} Kinesis records")

    for record in records:
        # Kinesis payloads are base64-encoded
        raw     = base64.b64decode(record['kinesis']['data']).decode('utf-8')
        payload = json.loads(raw)

        tenant_id = payload.get('tenantId')
        if not tenant_id:
            print("Skipping — missing tenantId")
            continue

        # Score the event for anomalies
        score = invoke_sagemaker(payload.get('metric', {}))
        print(f"tenant={tenant_id} anomaly_score={score:.3f}")

        if score >= ANOMALY_THRESHOLD:
            write_alert(tenant_id, payload, score)

    return {'statusCode': 200, 'processed': len(records)}


def invoke_sagemaker(metric: dict) -> float:
    """Send metric data to SageMaker endpoint, return anomaly score 0–1."""
    try:
        response = sagemaker.invoke_endpoint(
            EndpointName=SAGEMAKER_ENDPOINT,
            ContentType='application/json',
            Body=json.dumps(metric),
        )
        result = json.loads(response['Body'].read())
        return float(result.get('score', 0.0))
    except Exception as e:
        # Never let ML failures break the pipeline
        print(f"SageMaker error (non-fatal): {e}")
        return 0.0


def write_alert(tenant_id: str, payload: dict, score: float):
    """Persist a confirmed anomaly alert to DynamoDB."""
    now      = datetime.now(timezone.utc)
    severity = 'critical' if score > 0.9 else 'warning'

    alert_table.put_item(Item={
        'tenantId':  tenant_id,
        'alertId':   str(uuid.uuid4()),
        'severity':  severity,
        'score':     str(round(score, 4)),
        'payload':   json.dumps(payload),
        'createdAt': now.isoformat(),
        # TTL: auto-delete alerts after 7 days
        'ttl': int(now.timestamp()) + (7 * 86_400),
    })
    print(f"Alert written: tenant={tenant_id} severity={severity}")
