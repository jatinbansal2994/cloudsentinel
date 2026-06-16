"""
api-handler/index.py
────────────────────
REST API handler for the React dashboard.

Routes:
  GET  /alerts              → list recent anomaly alerts for the calling tenant
  GET  /tenants             → get the calling tenant's config
  POST /tenants             → create / update tenant config
  POST /ingest              → accept telemetry and put it on Kinesis
  GET  /admin/tenants       → [admin] list all tenants
  POST /admin/tenants       → [admin] create a new tenant + Cognito user
  GET  /admin/alerts        → [admin] cross-tenant alert list

tenantId is extracted from the Cognito JWT automatically — regular tenants can
ONLY see their own data. Admin routes require the caller to be in ADMIN_GROUP.
"""
import json
import os
import boto3
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
kinesis  = boto3.client('kinesis')
cognito  = boto3.client('cognito-idp')

TENANT_TABLE   = os.environ['TENANT_TABLE']
ALERT_TABLE    = os.environ['ALERT_TABLE']
KINESIS_STREAM = os.environ.get('KINESIS_STREAM_NAME', 'cloudsentinel-telemetry')
USER_POOL_ID   = os.environ.get('USER_POOL_ID', '')
ADMIN_GROUP    = os.environ.get('ADMIN_GROUP', 'cloudsentinel-admins')

tenant_table = dynamodb.Table(TENANT_TABLE)
alert_table  = dynamodb.Table(ALERT_TABLE)


def handler(event, context):
    method    = event.get('httpMethod', '')
    path      = event.get('path', '')
    claims    = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
    tenant_id = claims.get('custom:tenantId', 'unknown')

    try:
        if path == '/alerts'         and method == 'GET':  return get_alerts(tenant_id)
        if path == '/tenants'        and method == 'GET':  return get_tenant(tenant_id)
        if path == '/tenants'        and method == 'POST':
            return create_tenant(tenant_id, json.loads(event.get('body') or '{}'))
        if path == '/ingest'         and method == 'POST':
            return ingest(tenant_id, json.loads(event.get('body') or '{}'))

        # Admin routes — is_admin checked inside each function
        if path == '/admin/tenants'  and method == 'GET':
            return admin_list_tenants(claims)
        if path == '/admin/tenants'  and method == 'POST':
            return admin_create_tenant(claims, json.loads(event.get('body') or '{}'))
        if path == '/admin/alerts'   and method == 'GET':
            return admin_list_alerts(claims)

        return respond(404, {'error': 'Route not found'})
    except Exception as e:
        print(f"Unhandled error: {e}")
        return respond(500, {'error': 'Internal server error'})


# ── Helpers ────────────────────────────────────────────────────────────────

def is_admin(claims: dict) -> bool:
    groups = claims.get('cognito:groups', [])
    if isinstance(groups, str):
        groups = [groups]
    return ADMIN_GROUP in groups


def respond(status: int, body: dict):
    return {
        'statusCode': status,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps(body, default=str),
    }


# ── Tenant routes ──────────────────────────────────────────────────────────

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
        PartitionKey=tenant_id,
    )
    return respond(202, {'message': 'Accepted'})


# ── Admin routes ───────────────────────────────────────────────────────────

def admin_list_tenants(claims: dict):
    if not is_admin(claims):
        return respond(403, {'error': 'Forbidden'})
    items = tenant_table.scan(
        FilterExpression=Attr('sk').eq('CONFIG'),
    ).get('Items', [])
    items.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
    return respond(200, {'tenants': items})


def admin_create_tenant(claims: dict, body: dict):
    if not is_admin(claims):
        return respond(403, {'error': 'Forbidden'})

    email    = (body.get('email') or '').strip()
    name     = body.get('name', 'Unnamed Tenant')
    plan     = body.get('plan', 'free')
    password = (body.get('password') or '').strip()

    if not email or not password:
        return respond(400, {'error': 'email and password are required'})

    # Derive a stable tenantId from the email prefix
    prefix    = email.split('@')[0].lower().replace('.', '-').replace('+', '-')
    tenant_id = f'tenant-{prefix}'

    # Create Cognito user (suppress the welcome email — admin sets creds directly)
    cognito.admin_create_user(
        UserPoolId=USER_POOL_ID,
        Username=email,
        UserAttributes=[
            {'Name': 'email',             'Value': email},
            {'Name': 'email_verified',    'Value': 'true'},
            {'Name': 'custom:tenantId',   'Value': tenant_id},
        ],
        MessageAction='SUPPRESS',
    )

    # Set a permanent password so the user doesn't hit FORCE_CHANGE_PASSWORD
    cognito.admin_set_user_password(
        UserPoolId=USER_POOL_ID,
        Username=email,
        Password=password,
        Permanent=True,
    )

    # Persist tenant config
    tenant_table.put_item(Item={
        'tenantId':  tenant_id,
        'sk':        'CONFIG',
        'name':      name,
        'plan':      plan,
        'email':     email,
        'createdAt': datetime.now(timezone.utc).isoformat(),
    })

    return respond(201, {'tenantId': tenant_id, 'email': email})


def admin_list_alerts(claims: dict):
    if not is_admin(claims):
        return respond(403, {'error': 'Forbidden'})
    items = alert_table.scan(Limit=200).get('Items', [])
    items.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
    return respond(200, {'alerts': items})
