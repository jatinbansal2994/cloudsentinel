"""
api-handler/index.py
────────────────────
REST API handler for the React dashboard.

Routes:
  GET  /alerts   → list recent anomaly alerts for the calling tenant
  GET  /tenants  → get the calling tenant's config
  POST /tenants  → create / update tenant config
  POST /ingest   → accept telemetry and put it on Kinesis

tenantId is extracted from the Cognito JWT automatically — tenants can
ONLY see their own data, enforced at this layer.
"""
import json
import os
import boto3
from datetime import datetime, timezone

dynamodb     = boto3.resource('dynamodb')
kinesis      = boto3.client('kinesis')

TENANT_TABLE       = os.environ['TENANT_TABLE']
ALERT_TABLE        = os.environ['ALERT_TABLE']
KINESIS_STREAM     = os.environ.get('KINESIS_STREAM_NAME', 'cloudsentinel-telemetry')

tenant_table = dynamodb.Table(TENANT_TABLE)
alert_table  = dynamodb.Table(ALERT_TABLE)


def handler(event, context):
    method    = event.get('httpMethod', '')
    path      = event.get('path', '')
    claims    = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
    tenant_id = claims.get('custom:tenantId', 'unknown')

    try:
        if path == '/alerts'  and method == 'GET':  return get_alerts(tenant_id)
        if path == '/tenants' and method == 'GET':  return get_tenant(tenant_id)
        if path == '/tenants' and method == 'POST':
            return create_tenant(tenant_id, json.loads(event.get('body') or '{}'))
        if path == '/ingest'  and method == 'POST':
            return ingest(tenant_id, json.loads(event.get('body') or '{}'))
        return respond(404, {'error': 'Route not found'})
    except Exception as e:
        print(f"Unhandled error: {e}")
        return respond(500, {'error': 'Internal server error'})


def get_alerts(tenant_id: str):
    items = alert_table.query(
        KeyConditionExpression='tenantId = :t',
        ExpressionAttributeValues={':t': tenant_id},
        Limit=50,
        ScanIndexForward=False,  # newest first
    ).get('Items', [])
    return respond(200, {'alerts': items})


def get_tenant(tenant_id: str):
    item = tenant_table.get_item(
        Key={'tenantId': tenant_id, 'sk': 'CONFIG'}
    ).get('Item', {})
    return respond(200, {'tenant': item})


def create_tenant(tenant_id: str, body: dict):
    tenant_table.put_item(Item={
        'tenantId':  tenant_id,
        'sk':        'CONFIG',
        'name':      body.get('name', 'Unnamed Tenant'),
        'plan':      body.get('plan', 'free'),
        'createdAt': datetime.now(timezone.utc).isoformat(),
    })
    return respond(201, {'message': 'Tenant created', 'tenantId': tenant_id})


def ingest(tenant_id: str, body: dict):
    """Put a telemetry event on Kinesis. Kinesis uses tenantId as partition key
    so all events from the same tenant go to the same shard (preserves order)."""
    record = json.dumps({**body, 'tenantId': tenant_id})
    kinesis.put_record(
        StreamName=KINESIS_STREAM,
        Data=record.encode('utf-8'),
        PartitionKey=tenant_id,   # per-tenant shard isolation
    )
    return respond(202, {'message': 'Accepted'})


def respond(status: int, body: dict):
    return {
        'statusCode': status,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps(body, default=str),
    }
