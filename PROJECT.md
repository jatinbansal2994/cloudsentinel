# CloudSentinel — Project Status

## What is this
Multi-tenant SaaS observability platform on AWS.
Tenants send telemetry → Kinesis streams it → Lambda processes it →
SageMaker scores anomalies → DynamoDB stores alerts → React dashboard shows them.

## Tech Stack
- IaC:       AWS CDK (Python 3.11)
- Streaming: Kinesis Data Streams (2 shards, per-tenant partitioning)
- Compute:   Lambda Python 3.11 (stream-processor + api-handler)
- ML:        SageMaker endpoint running Isolation Forest
- DB:        DynamoDB (on-demand), S3 + Athena, ElastiCache
- Auth:      Cognito (multi-tenant, tenantId in JWT)
- Alerts:    SNS + EventBridge
- Frontend:  React → S3 + CloudFront
- CI/CD:     GitHub Actions

## Folder Structure
cloudsentinel/
  app.py                    CDK entrypoint — run: cdk deploy --all
  requirements.txt          CDK Python deps
  cdk.json                  CDK config
  stacks/                   One file per AWS concern
    network_stack.py        VPC
    auth_stack.py           Cognito
    storage_stack.py        DynamoDB + S3
    streaming_stack.py      Kinesis
    compute_stack.py        Lambda + API Gateway
    ml_stack.py             SageMaker role
    alerting_stack.py       SNS + EventBridge
    frontend_stack.py       CloudFront + S3
  lambda/
    stream-processor/       Kinesis -> SageMaker -> DynamoDB
    api-handler/            REST API for React
  ml/
    training/train.py       Train Isolation Forest
    inference/serve.py      Flask server for SageMaker
  docker/
    docker-compose.yml      Local dev stack

## Current Status
[x] Phase 0: Python CDK project structure
[x] Phase 1: AWS account setup + cdk bootstrap
[x] Phase 2: cdk deploy --all (Streaming stack failing — see Known Issues)
[ ] Phase 3: Train model + deploy SageMaker endpoint
[ ] Phase 4: React frontend
[ ] Phase 5: Docker + CI/CD
[ ] Phase 6: Testing + polish

## Bugs Fixed
- compute_stack.py line 128: `**auth_opts.__dict__` leaked jsii internal `_values` field
  → Fixed: pass `authorization_type` and `authorizer` as explicit kwargs to `add_method()`
- S3Origin deprecation warning in frontend_stack.py (harmless for now, fix later)
  → Replace `S3Origin` with `S3BucketOrigin` or `S3StaticWebsiteOrigin`



## Environment Notes
- Region: ap-south-1 (Mumbai) — switch to us-east-1 if instability continues
- Always activate venv before working: source .venv/bin/activate
- CDK installed via sudo npm (system Node via NodeSource apt repo)
- venv does NOT affect aws/cdk CLI commands — only pip/python

## First Time Setup
python3 -m venv .venv
source .venv/bin/activate      # Mac/Linux
pip install -r requirements.txt
sudo npm install -g aws-cdk    # use sudo — system Node via NodeSource
cdk bootstrap
cdk deploy --all

## Run Locally
cd ml/training && python train.py
cd ../../docker && docker compose up

PASTE THIS FILE AT THE START OF EVERY CLAUDE SESSION.
