"""
scripts/get_token.py
────────────────────
Authenticates with Cognito and prints your ID token so you can
pass it to send_telemetry.py.

Usage:
  source scripts/post-deploy.sh   ← sets CLOUDSENTINEL_USER_POOL_ID / CLIENT_ID
  python scripts/get_token.py

Or pass values explicitly:
  CLOUDSENTINEL_USER_POOL_ID=us-east-1_xxx \
  CLOUDSENTINEL_CLIENT_ID=yyy \
  python scripts/get_token.py
"""
import os
import sys
import getpass
import boto3

USER_POOL_ID = os.environ.get("CLOUDSENTINEL_USER_POOL_ID", "")
CLIENT_ID    = os.environ.get("CLOUDSENTINEL_CLIENT_ID", "")

if not USER_POOL_ID or not CLIENT_ID:
    print("Error: CLOUDSENTINEL_USER_POOL_ID and CLOUDSENTINEL_CLIENT_ID must be set.")
    print("Run:  source scripts/post-deploy.sh")
    sys.exit(1)

print(f"User Pool: {USER_POOL_ID}")
username = input("Email: ").strip()
password = getpass.getpass("Password: ")

client = boto3.client("cognito-idp", region_name="us-east-1")

try:
    resp = client.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": username, "PASSWORD": password},
        ClientId=CLIENT_ID,
    )
    token = resp["AuthenticationResult"]["IdToken"]
    print("\nID Token (use this with --token):\n")
    print(token)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
