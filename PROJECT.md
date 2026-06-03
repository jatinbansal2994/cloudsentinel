# CloudSentinel — Project Status

## What is this
Multi-tenant SaaS observability platform on AWS.
Tenants send telemetry → Kinesis streams it → Lambda processes it →
SageMaker scores anomalies → DynamoDB stores alerts → React dashboard shows them.

## Tech Stack
- IaC:       AWS CDK (Python 3.11)
- Streaming: Kinesis Data Streams (2 shards, per-tenant partitioning)
- Compute:   Lambda Python 3.11 (stream-processor + api-handler)
- ML:        SageMaker endpoint running Isolation Forest (sklearn 1.2-1 container)
- DB:        DynamoDB (on-demand), S3 + Athena, ElastiCache
- Auth:      Cognito (multi-tenant, tenantId in JWT)
- Alerts:    SNS (stream-processor publishes on every anomaly) + EventBridge
- Frontend:  React → S3 + CloudFront (OAC)
- CI/CD:     GitHub Actions

## Folder Structure
cloudsentinel/
  app.py                    CDK entrypoint — run: cdk deploy --all
  requirements.txt          CDK Python deps
  cdk.json                  CDK config (region: us-east-1)
  stacks/                   One file per AWS concern
    network_stack.py        VPC (2 AZs, 1 NAT gateway)
    auth_stack.py           Cognito (tenantId custom JWT attribute)
    storage_stack.py        DynamoDB (tenants + alerts tables) + S3 data lake
    streaming_stack.py      Kinesis (2 shards, 24h retention)
    compute_stack.py        Lambda + API Gateway (all routes Cognito-protected)
    ml_stack.py             SageMaker CfnModel + CfnEndpointConfig + CfnEndpoint
    alerting_stack.py       SNS topic + EventBridge custom bus
    frontend_stack.py       CloudFront (OAC) + S3
  lambda/
    stream-processor/       Kinesis → SageMaker → DynamoDB → SNS
    api-handler/            REST API for React (GET /alerts, GET|POST /tenants, POST /ingest)
  ml/
    training/train.py       Train Isolation Forest, package model.tar.gz, upload to S3
    inference/serve.py      SageMaker script-mode inference (model_fn/input_fn/predict_fn/output_fn)
  docker/
    docker-compose.yml      Local dev stack (LocalStack + Redis + inference container)

## Current Status
[x] Phase 0: Python CDK project structure
[x] Phase 1: AWS account setup + cdk bootstrap
[x] Phase 2: cdk deploy --all (base stacks deployed)
[x] Phase 3: Train model + deploy SageMaker endpoint
      [x] ml_stack CDK code complete (CfnModel + CfnEndpoint)
      [x] train.py + serve.py complete
      [x] model.tar.gz trained and uploaded to S3 (trained with sklearn==1.2.1 via Python 3.11 venv)
      [x] All 7 stacks deployed: Network, Auth, Storage, Streaming, ML, Alerting, Compute
      [x] SageMaker endpoint InService
[x] Phase 4: React frontend
      [x] Vite + React scaffolded in frontend/
      [x] Tailwind CSS configured
      [x] Cognito auth (login/logout, JWT via amazon-cognito-identity-js)
      [x] Alerts page (GET /alerts — table with severity badges)
      [x] Tenants page (GET /tenants + POST /tenants form)
      [x] Ingest page (POST /ingest — editable JSON payload)
      [x] Production build clean (vite build → dist/)
      [ ] Deploy: fill frontend/.env, run cdk deploy CloudSentinel-Frontend, then sync dist/ to S3
[ ] Phase 5: Docker + CI/CD
[ ] Phase 6: Testing + polish

## Deployed Stacks (us-east-1, account 187516374644)
- CloudSentinel-Network    → DEPLOYED
- CloudSentinel-Auth       → DEPLOYED
- CloudSentinel-Storage    → DEPLOYED (bucket: cloudsentinel-datalake-187516374644)
- CloudSentinel-Streaming  → DEPLOYED (stream: cloudsentinel-telemetry)
- CloudSentinel-ML         → DEPLOYED (endpoint InService)
- CloudSentinel-Alerting   → DEPLOYED
- CloudSentinel-Compute    → DEPLOYED
- CloudSentinel-Frontend   → NOT DEPLOYED

## Training Notes
- Always use `.venv-training` (Python 3.11) to retrain — sklearn must be 1.2.1 to match the SageMaker container
- `.venv` (Python 3.12) is for CDK only
- Retrain command: `source .venv-training/bin/activate && cd ml/training && python3 train.py`

## Bugs Fixed (all sessions)
- compute_stack.py: **auth_opts.__dict__ leaked jsii internal _values field
  → Fixed: pass authorization_type and authorizer as explicit kwargs to add_method()
- compute_stack.py: /alerts and /tenants routes had NO Cognito authorizer (security bug)
  → Fixed: all 4 API routes now require a valid Cognito JWT
- frontend_stack.py: S3Origin deprecated
  → Fixed: replaced with S3BucketOrigin.with_origin_access_control() (OAC)
- alerting_stack.py: SNS topic created but never published to (dead code)
  → Fixed: stream-processor Lambda now publishes to SNS on every confirmed anomaly
- alerting_stack.py: alert_table parameter accepted but never used
  → Fixed: removed unused parameter
- ml/training/requirements.txt: boto3 and joblib missing
  → Fixed: added boto3>=1.34.0 and joblib>=1.3.0
- ml_stack.py: IAM Role description had em dash (—) rejected by AWS IAM
  → Fixed: replaced with plain hyphen (-)
- ml_stack.py: ml.t3.medium no longer valid SageMaker instance type
  → Fixed: changed to ml.t2.medium
- ml_stack.py: race condition — SageMaker model created before IAM policy attached
  → Fixed: added node.add_dependency(role.DefaultPolicy) on CfnModel
- ml/training/train.py: --bucket arg required, inconvenient
  → Fixed: auto-detects bucket from CloudSentinel-Storage CloudFormation output
- ml/inference/serve.py: str | bytes annotation incompatible with Python 3.9 container
  → Fixed: added from __future__ import annotations
- ml/training/train.py: serve.py packaged at tarball root, container expects code/ subdirectory
  → Fixed: serve.py now placed at code/serve.py inside model.tar.gz
- ml_stack.py: SAGEMAKER_SUBMIT_DIRECTORY not set, container used broken pip install path
  → Fixed: added SAGEMAKER_SUBMIT_DIRECTORY=/opt/ml/model/code
- .gitignore: __pycache__ files were already tracked in git
  → Fixed: git rm --cached; added *.swp, cdk.context.json, model artifacts to .gitignore

## Environment Notes
- Region: us-east-1 (set in cdk.json)
- AWS Account: 187516374644
- Always activate venv before working: source .venv/bin/activate
- CDK installed locally via npm install (package.json)
- cdk.context.json is gitignored — auto-generated per account on first cdk synth
- model.tar.gz is gitignored — generated by train.py and lives in S3

## First Time Setup (per developer)
python3 -m venv .venv
source .venv/bin/activate       # Mac/Linux
pip install -r requirements.txt
npm install                     # installs aws-cdk CLI into node_modules/
npx cdk bootstrap               # one-time per AWS account/region
cdk deploy --all

## Run Locally
cd ml/training && python train.py --no-upload   # dry-run, no S3
cd ../../docker && docker compose up

## Stack Dependency Order
Storage → ML → Alerting → Compute → Frontend
(enforced via add_dependency() in app.py)

PASTE THIS FILE AT THE START OF EVERY CLAUDE SESSION.
