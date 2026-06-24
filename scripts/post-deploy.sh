#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# scripts/post-deploy.sh
#
# Run AFTER `cdk deploy --all` to auto-populate every config file and export
# the env vars the helper scripts need.
#
# Usage:
#   source scripts/post-deploy.sh        ← 'source' so exports persist in shell
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

REGION="us-east-1"

_out() {
    aws cloudformation describe-stacks \
        --stack-name "$1" \
        --region "$REGION" \
        --query "Stacks[0].Outputs[?OutputKey=='$2'].OutputValue" \
        --output text
}

echo "Reading CloudFormation outputs..."

# All values we need live in the Frontend stack outputs
USER_POOL_ID=$(_out "CloudSentinel-Frontend" "UserPoolId")
CLIENT_ID=$(_out    "CloudSentinel-Frontend" "UserPoolClientId")
API_ENDPOINT=$(_out "CloudSentinel-Frontend" "ApiEndpoint")
CF_URL=$(_out       "CloudSentinel-Frontend" "CloudFrontUrl")
SITE_BUCKET=$(_out  "CloudSentinel-Frontend" "SiteBucketName")

# Strip trailing slash from API endpoint (CDK adds one)
API_ENDPOINT="${API_ENDPOINT%/}"

# CloudFront distribution ID (not a stack output — look it up by domain)
CF_DOMAIN="${CF_URL#https://}"
CF_DIST_ID=$(aws cloudfront list-distributions \
    --query "DistributionList.Items[?DomainName=='${CF_DOMAIN}'].Id" \
    --output text)

# AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo ""
echo "Got all values:"
echo "  User Pool ID:   $USER_POOL_ID"
echo "  App Client ID:  $CLIENT_ID"
echo "  API Endpoint:   $API_ENDPOINT"
echo "  CloudFront URL: $CF_URL"
echo "  Site Bucket:    $SITE_BUCKET"
echo "  CF Dist ID:     $CF_DIST_ID"
echo "  Account ID:     $ACCOUNT_ID"

# ── 1. Write frontend/.env ────────────────────────────────────────────────────
cat > frontend/.env << EOF
VITE_USER_POOL_ID=$USER_POOL_ID
VITE_USER_POOL_CLIENT_ID=$CLIENT_ID
VITE_API_ENDPOINT=$API_ENDPOINT
EOF
echo ""
echo "Written: frontend/.env"

# ── 2. Write PROJECT.md ───────────────────────────────────────────────────────
cat > PROJECT.md << EOF
# CloudSentinel — Project Status

## What is this
Multi-tenant SaaS observability platform on AWS.
Tenants send telemetry → Kinesis streams it → Lambda processes it →
SageMaker scores anomalies → DynamoDB stores alerts → React dashboard shows them.

## Tech Stack
- IaC:       AWS CDK (Python)
- Streaming: Kinesis Data Streams (2 shards, per-tenant partitioning)
- Compute:   Lambda Python (stream-processor + api-handler)
- ML:        SageMaker endpoint running Isolation Forest (sklearn 1.2.1 container)
- DB:        DynamoDB (on-demand), S3 data lake
- Auth:      Cognito (multi-tenant, tenantId in JWT, admins group)
- Alerts:    SNS (stream-processor publishes on every anomaly, per-tenant filter)
- Frontend:  React (Vite + Tailwind) → S3 + CloudFront (OAC)

## Folder Structure
cloudsentinel/
  app.py                    CDK entrypoint — run: cdk deploy --all
  requirements.txt          CDK Python deps
  cdk.json                  CDK config (region: us-east-1)
  stacks/
    network_stack.py        VPC (2 AZs, 1 NAT gateway)
    auth_stack.py           Cognito (tenantId custom JWT attribute, admins group)
    storage_stack.py        DynamoDB (tenants + alerts tables) + S3 data lake
    streaming_stack.py      Kinesis (2 shards, 24h retention, RemovalPolicy.DESTROY)
    compute_stack.py        Lambda + API Gateway (all routes Cognito-protected)
    ml_stack.py             SageMaker CfnModel + CfnEndpointConfig + CfnEndpoint
    alerting_stack.py       SNS topic + EventBridge custom bus
    frontend_stack.py       CloudFront (OAC) + S3
  lambda/
    stream-processor/       Kinesis → SageMaker → DynamoDB → SNS
    api-handler/            REST API (tenant routes + admin routes)
  ml/
    training/train.py       Train Isolation Forest, package model.tar.gz, upload to S3
    inference/serve.py      SageMaker script-mode inference (decision_function scoring)
  frontend/
    src/pages/Alerts.jsx    Anomaly alert table (severity, score, timestamp)
    src/pages/Tenants.jsx   My Account (display name + plan)
    src/pages/Ingest.jsx    Send test telemetry from browser
    src/pages/Admin.jsx     Admin: manage all tenants, view cross-tenant alerts
  scripts/
    post-deploy.sh          Run after cdk deploy --all to auto-fill all config
    get_token.py            Fetch Cognito JWT for API / telemetry script
    send_telemetry.py       Stream real/simulated/anomaly metrics to pipeline
  docs/
    sending-telemetry.md    Guide for friends sending their PC metrics
  tests/
    test_stream_processor.py  24 unit tests
    test_api_handler.py       28 unit tests
    test_serve.py             15 unit tests

## Current Status
[x] Phase 0: Python CDK project structure
[x] Phase 1: AWS account setup + cdk bootstrap
[x] Phase 2: cdk deploy --all (base stacks deployed)
[x] Phase 3: Train model + deploy SageMaker endpoint
[x] Phase 4: React frontend
[x] Phase 4.5: Bug fixes post-deploy
[x] Phase 5: Admin panel
[x] Phase 6: Docker + CI/CD
[x] Phase 7: Testing + polish

## Deployed Resources (us-east-1, account $ACCOUNT_ID)
- CloudSentinel-Network    → DEPLOYED
- CloudSentinel-Auth       → DEPLOYED (pool: $USER_POOL_ID)
- CloudSentinel-Storage    → DEPLOYED (bucket: cloudsentinel-datalake-$ACCOUNT_ID)
- CloudSentinel-Streaming  → DEPLOYED (stream: cloudsentinel-telemetry)
- CloudSentinel-ML         → DEPLOYED (endpoint: cloudsentinel-anomaly-detector, InService)
- CloudSentinel-Alerting   → DEPLOYED (topic: cloudsentinel-alerts)
- CloudSentinel-Compute    → DEPLOYED (api: ${API_ENDPOINT#https://})
- CloudSentinel-Frontend   → DEPLOYED ($CF_URL)

## Key IDs (us-east-1)
- User Pool ID:    $USER_POOL_ID
- App Client ID:   $CLIENT_ID
- API base URL:    $API_ENDPOINT
- CloudFront URL:  $CF_URL
- S3 Site Bucket:  $SITE_BUCKET
- CF Dist ID:      $CF_DIST_ID

## Training Notes
- Always use \`.venv-training\` (Python 3.11) to retrain — sklearn must be 1.2.1 to match SageMaker container
- \`.venv\` (Python 3.12) is for CDK only
- Retrain command: \`source .venv-training/bin/activate && cd ml/training && python3 train.py\`
- After retrain: must delete SageMaker endpoint/config/model manually before cdk deploy CloudSentinel-ML
  (CDK does not detect S3 content changes at the same URI)

## Scoring Notes
- serve.py uses decision_function (NOT score_samples)
- decision_function: positive = normal, negative = anomaly
- Severity thresholds: critical < -0.04 | high < -0.01 | medium < 0.03 | normal ≥ 0.03
- Normal machine data (CPU 1-15%) scores ~+0.08, well above threshold

## Environment Notes
- Region: us-east-1 (set in cdk.json)
- AWS Account: $ACCOUNT_ID
- Always activate venv before working: source .venv/bin/activate
- CDK installed locally via npm install (package.json)
- cdk.context.json is gitignored — auto-generated per account on first cdk synth
- model.tar.gz is gitignored — generated by train.py and lives in S3
- API URL changes on every Compute stack redeploy — re-run post-deploy.sh

## Stack Dependency Order
Network, Auth, Storage → Streaming, ML, Alerting → Compute → Frontend
(enforced via add_dependency() in app.py)

PASTE THIS FILE AT THE START OF EVERY CLAUDE SESSION.
EOF
echo "Written: PROJECT.md"

# ── 3. Export env vars for helper scripts ─────────────────────────────────────
export CLOUDSENTINEL_USER_POOL_ID="$USER_POOL_ID"
export CLOUDSENTINEL_CLIENT_ID="$CLIENT_ID"
export CLOUDSENTINEL_API_ENDPOINT="$API_ENDPOINT/ingest"
echo ""
echo "Exported shell vars:"
echo "  CLOUDSENTINEL_USER_POOL_ID"
echo "  CLOUDSENTINEL_CLIENT_ID"
echo "  CLOUDSENTINEL_API_ENDPOINT"

# ── 4. Print next steps ───────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Next steps:"
echo ""
echo "  1. Build and deploy the frontend:"
echo "       cd frontend && npm install && npm run build && cd .."
echo "       aws s3 sync frontend/dist/ s3://$SITE_BUCKET --delete"
echo "       aws cloudfront create-invalidation --distribution-id $CF_DIST_ID --paths '/*'"
echo ""
echo "  2. Create your admin Cognito user (first time only):"
echo "       See README.md → Deploy → Step 5"
echo ""
echo "  3. Send telemetry:"
echo "       python scripts/get_token.py"
echo "       python scripts/send_telemetry.py --token <token> --interval 10"
echo ""
echo "  Dashboard: $CF_URL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
