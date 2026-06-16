"""
scripts/get_token.py
────────────────────
Authenticates with Cognito and prints your ID token so you can
pass it to send_telemetry.py.

Usage:
  python scripts/get_token.py
"""
import json
import sys

USER_POOL_ID  = "us-east-1_7edoTifa1"
CLIENT_ID     = "32vr8rg7iq0jbdtrlqqhaf2v1o"

USERNAME      = "jatinbansal2994@gmail.com"
PASSWORD      = "CloudSentinel@123"

import boto3

client = boto3.client("cognito-idp", region_name="us-east-1")

try:
    resp = client.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": USERNAME, "PASSWORD": PASSWORD},
        ClientId=CLIENT_ID,
    )
    token = resp["AuthenticationResult"]["IdToken"]
    print("ID Token (use this with --token):\n")
    print(token)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
