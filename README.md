# CloudSentinel

Multi-tenant SaaS observability platform on AWS. Tenants push telemetry to a REST API → Kinesis buffers it → Lambda scores each event with an Isolation Forest on SageMaker → anomalies are stored in DynamoDB and published to SNS → a React dashboard shows live alerts per tenant.

## Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Deploy](#deploy)
- [Frontend](#frontend)
- [Admin Panel](#admin-panel)
- [Running Locally with Docker](#running-locally-with-docker)
- [CI/CD](#cicd)
- [Sending Telemetry](#sending-telemetry)
- [Email Alerts](#email-alerts)
- [Running Tests](#running-tests)
- [Retraining the Model](#retraining-the-model)
- [Teardown](#teardown)
- [Common Issues](#common-issues)
- [Project Structure](#project-structure)

---

## Architecture

```
Client / Tenant
      │
      ▼
API Gateway  (Cognito JWT auth)
      │
      ▼
Lambda: api-handler          ←── GET /alerts  GET|POST /tenants
      │  POST /ingest
      ▼
Kinesis Data Stream  (2 shards, 24 h retention)
      │
      ▼
Lambda: stream-processor
      ├── SageMaker endpoint  (Isolation Forest — anomaly score)
      ├── DynamoDB            (persist alert record)
      └── SNS topic           (fan-out email notifications)

React Dashboard  (S3 + CloudFront)  ←── reads DynamoDB via api-handler
```

**Stack:** AWS CDK (Python) · Kinesis · Lambda · SageMaker (sklearn 1.2.1) · DynamoDB · Cognito · SNS · EventBridge · CloudFront · React + Tailwind CSS

### Severity mapping

Alerts are scored using Isolation Forest's `decision_function`:

| Score range | Severity |
|-------------|----------|
| ≥ 0.03      | No alert (normal) |
| 0.00 – 0.03 | Medium |
| -0.04 – -0.01 | High |
| < -0.04     | Critical |

---

## Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| Python 3.12 | CDK and Lambda runtime | `python3 --version` |
| Python 3.11 | ML training only | `python3.11 --version` |
| Node.js | 18+ | `node --version` |
| AWS CLI | v2 | `aws --version` |
| AWS account | admin IAM permissions | `aws sts get-caller-identity` |

> **Why two Python versions?** The SageMaker sklearn 1.2.1 container has no pre-built wheel for Python 3.12. A dedicated Python 3.11 training venv sidesteps this — CDK still runs on Python 3.12.

### Install Python 3.11

**Ubuntu / Debian:**
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
```

**macOS:**
```bash
brew install python@3.11
```

### Configure AWS credentials

#### 1. Create an Access Key

1. Log in to [console.aws.amazon.com](https://console.aws.amazon.com)
2. Top-right → your name → **Security credentials**
3. Scroll to **Access keys** → **Create access key**
4. Choose **CLI** → create → copy both values

> For a personal / dev account attach the **AdministratorAccess** policy to your IAM user — CDK needs broad permissions to create IAM roles, Lambda functions, S3 buckets, etc.

#### 2. Run aws configure

```bash
aws configure
```

Fill in the four prompts:

```
AWS Access Key ID:     <your access key>
AWS Secret Access Key: <your secret key>
Default region name:   us-east-1
Default output format: json
```

#### 3. Verify

```bash
aws sts get-caller-identity
```

Should print your account ID, user ID, and ARN. If this command succeeds, CDK will work.

---

## Setup

### 1. Clone the repo

```bash
git clone git@github.com:jatinbansal2994/cloudsentinel.git
cd cloudsentinel
```

### 2. CDK virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
npm install                   # installs aws-cdk CLI into node_modules/
```

### 3. Bootstrap CDK

One-time per AWS account + region:

```bash
npx cdk bootstrap
```

### 4. ML training virtual environment

```bash
python3.11 -m venv .venv-training
source .venv-training/bin/activate

pip install "numpy>=1.24,<2.0" scikit-learn==1.2.1 pandas boto3 joblib
```

> **Note:** The PyPI package is called `scikit-learn` — do **not** run `pip install sklearn`,
> that package is deprecated and will fail. Once installed, it is imported as `sklearn` in Python.

```bash
# Verify the version matches the SageMaker container
python3 -c "import sklearn; print(sklearn.__version__)"
# Expected: 1.2.1

deactivate
```

---

## Deploy

All commands run from the repo root.

### Step 1 — Base infrastructure

```bash
source .venv/bin/activate
npx cdk deploy CloudSentinel-Network CloudSentinel-Auth CloudSentinel-Storage \
           CloudSentinel-Streaming CloudSentinel-Alerting --require-approval never
```

### Step 2 — Train and upload the model

`train.py` auto-detects the S3 bucket from the Storage stack output.

```bash
source .venv-training/bin/activate
cd ml/training && python3 train.py && cd ../..
deactivate
```

### Step 3 — ML endpoint

```bash
source .venv/bin/activate
npx cdk deploy CloudSentinel-ML --require-approval never
```

SageMaker pulls the container image on first deploy — allow 5–8 minutes. Confirm before continuing:

```bash
aws sagemaker describe-endpoint \
  --endpoint-name cloudsentinel-anomaly-detector \
  --query "EndpointStatus" --output text
# Must return: InService
```

### Step 4 — Compute and frontend

```bash
npx cdk deploy CloudSentinel-Compute CloudSentinel-Frontend --require-approval never
```

### Step 5 — Create a tenant user

Each tenant needs a Cognito user with `custom:tenantId` set at creation time (the attribute is immutable after creation).

> **Important:** The email in `--username` and `Name="email",Value=` must be **exactly the same** — a typo between the two will cause `InvalidParameterException` and the user won't be created.

```bash
USER_POOL_ID=$(aws cloudformation describe-stacks --stack-name CloudSentinel-Auth \
  --query "Stacks[0].Outputs[?OutputKey=='UserPoolId'].OutputValue" --output text)

aws cognito-idp admin-create-user \
  --user-pool-id "$USER_POOL_ID" \
  --username tenant@example.com \
  --temporary-password TempPass123! \
  --message-action SUPPRESS \
  --user-attributes \
    Name="email",Value="tenant@example.com" \
    Name="email_verified",Value="true" \
    Name="custom:tenantId",Value="tenant-acme"

aws cognito-idp admin-set-user-password \
  --user-pool-id "$USER_POOL_ID" \
  --username tenant@example.com \
  --password SecurePass123! \
  --permanent
```

### Step 6 — Auto-populate config and deploy the frontend

`post-deploy.sh` reads all CloudFormation outputs and writes `frontend/.env`, `PROJECT.md`,
and exports the env vars the helper scripts need — all in one command:

```bash
source scripts/post-deploy.sh
```

Then build and sync (the script prints the exact commands with real values at the end):

```bash
cd frontend && npm install && npm run build && cd ..
aws s3 sync frontend/dist/ s3://<SiteBucket> --delete
aws cloudfront create-invalidation --distribution-id <CF_DIST_ID> --paths "/*"
```

> **Note:** Use `source` (not `bash`) so the exported env vars persist in your shell session
> and the helper scripts (`get_token.py`, `send_telemetry.py`) work without extra config.

### Step 7 — Verify all stacks

```bash
aws cloudformation list-stacks \
  --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE \
  --query "StackSummaries[?contains(StackName,'CloudSentinel')].{Name:StackName,Status:StackStatus}" \
  --output table
```

Expected: 8 stacks — Network, Auth, Storage, Streaming, ML, Alerting, Compute, Frontend.

---

## Frontend

The React dashboard (Vite + Tailwind CSS) lives in `frontend/`. It has four pages:

| Page | Who sees it | What it does |
|------|------------|-------------|
| **Alerts** | All tenants | Anomaly alerts scoped to your tenant — severity badge, score, timestamp |
| **Account** | All tenants | Your tenant display name and plan |
| **Ingest** | All tenants | Send a test telemetry event directly from the browser |
| **Admin** | Admins only | Create tenants, view cross-tenant alerts |

The **Admin** tab is only visible when the logged-in user's JWT contains `cognito:groups: ["cloudsentinel-admins"]`.

Log in with the email + password set in Step 5 above.

---

## Admin Panel

Admins can create new tenants and view all alerts across every tenant.

### Add a user to the admins group

```bash
USER_POOL_ID=$(aws cloudformation describe-stacks --stack-name CloudSentinel-Auth \
  --query "Stacks[0].Outputs[?OutputKey=='UserPoolId'].OutputValue" --output text)

aws cognito-idp admin-add-user-to-group \
  --user-pool-id "$USER_POOL_ID" \
  --username admin@example.com \
  --group-name cloudsentinel-admins
```

Once in the group, the **Admin** tab appears in the sidebar after the next login. From there you can create new tenants (which also creates their Cognito user in one step) and browse a cross-tenant alert feed.

---

## Running Locally with Docker

The frontend can be served locally without deploying to AWS. The Docker image does a production build and serves it via nginx on port 3000.

```bash
docker-compose up --build
# open http://localhost:3000
```

The container still talks to the real AWS API and Cognito — you need a valid `frontend/.env` with `VITE_API_ENDPOINT`, `VITE_USER_POOL_ID`, and `VITE_USER_POOL_CLIENT_ID`.

---

## CI/CD

A GitHub Actions workflow (`.github/workflows/deploy.yml`) runs on every push to `main`:

1. **deploy-backend** — runs `cdk deploy CloudSentinel-Compute` to update Lambda + API Gateway.
2. **deploy-frontend** — builds the React app and syncs to S3, then invalidates the CloudFront distribution. This job waits for the backend job to finish first.

### Required GitHub Secrets

| Secret | Where to get it |
|--------|----------------|
| `AWS_ACCESS_KEY_ID` | IAM user with CDK + S3 + CloudFront permissions |
| `AWS_SECRET_ACCESS_KEY` | Same IAM user |
| `VITE_API_ENDPOINT` | Compute stack output (`ApiUrl`) |
| `VITE_USER_POOL_ID` | Auth stack output (`UserPoolId`) |
| `VITE_USER_POOL_CLIENT_ID` | Auth stack output (`UserPoolClientId`) |
| `S3_SITE_BUCKET` | Frontend stack output (`SiteBucketName`) |
| `CF_DIST_ID` | Frontend stack output — CloudFront distribution ID |

---

## Sending Telemetry

See **[docs/sending-telemetry.md](docs/sending-telemetry.md)** for a full guide including how to stream your real machine's CPU and memory into the pipeline.

Quick start:

```bash
pip install psutil
source .venv/bin/activate
source scripts/post-deploy.sh        # exports pool IDs — skip if already done this session
python scripts/get_token.py          # prompts for email + password, prints token
python scripts/send_telemetry.py --token "<token>" --interval 10
```

---

## Email Alerts

The SNS topic `cloudsentinel-alerts` publishes every anomaly. Run this **once per tenant** after deploy to subscribe their email — they will only receive alerts for their own tenant:

```bash
TOPIC_ARN=$(aws cloudformation describe-stacks --stack-name CloudSentinel-Alerting \
  --query "Stacks[0].Outputs[?OutputKey=='AlertTopicArn'].OutputValue" --output text)

aws sns subscribe \
  --topic-arn "$TOPIC_ARN" \
  --protocol email \
  --notification-endpoint harshal@gmail.com \
  --attributes '{"FilterPolicy":"{\"tenantId\":[\"tenant-harshal\"]}"}'
```

Replace `harshal@gmail.com` and `tenant-harshal` with the email and tenant ID used in **Step 5**.

AWS sends a confirmation email to that address — **they must click the link** to activate the subscription. Once confirmed, anomaly emails arrive within ~30 seconds of detection.

---

## Running Tests

Unit tests cover both Lambda functions and the ML inference script. No AWS credentials needed — all AWS calls are mocked.

```bash
source .venv/bin/activate
pip install -r requirements-test.txt   # first time only — installs pytest
pytest
```

Expected output: **67 tests, ~0.3 s**.

| Test file | What it covers |
|-----------|---------------|
| `tests/test_stream_processor.py` | `severity()` thresholds, handler routing, SageMaker feature extraction, SNS publishing |
| `tests/test_api_handler.py` | All 7 API routes, `is_admin()`, 403/400 guards, tenant-ID derivation |
| `tests/test_serve.py` | `input_fn` (single/batch/bytes/missing features), `predict_fn`, `output_fn`, round-trip |

---

## Retraining the Model

Run whenever you change `ml/training/train.py` or `ml/inference/serve.py`:

```bash
source .venv-training/bin/activate
cd ml/training && python3 train.py && cd ../..
deactivate

source .venv/bin/activate
# Delete old SageMaker resources (CDK won't detect S3 content change)
aws sagemaker delete-endpoint --endpoint-name cloudsentinel-anomaly-detector
aws sagemaker delete-endpoint-config --endpoint-config-name cloudsentinel-endpoint-config
aws sagemaker delete-model --model-name cloudsentinel-isolation-forest

npx cdk destroy CloudSentinel-ML --force
npx cdk deploy CloudSentinel-ML --require-approval never
```

---

## Teardown

```bash
source .venv/bin/activate
npx cdk destroy --all --force
```

The Kinesis stream has `RemovalPolicy.DESTROY` and is deleted automatically. All other stateful resources (DynamoDB, S3) are also set to DESTROY.

---

## Common Issues

### `Resource already exists` — Kinesis stream

A previous destroy left the stream behind. Delete it and retry:

```bash
aws kinesis delete-stream --stream-name cloudsentinel-telemetry
npx cdk deploy CloudSentinel-Streaming
```

### `No module named 'distutils'` — installing sklearn

`.venv-training` was created with Python 3.12. Recreate it:

```bash
rm -rf .venv-training
python3.11 -m venv .venv-training
source .venv-training/bin/activate
pip install "numpy>=1.24,<2.0" scikit-learn==1.2.1 pandas boto3 joblib
```

### `numpy.dtype size changed` — binary incompatibility

numpy 2.x installed, incompatible with sklearn 1.2.1. Downgrade:

```bash
source .venv-training/bin/activate
pip install "numpy>=1.24,<2.0"
```

### All alerts showing as `critical`

The inference script was using `score_samples` instead of `decision_function`. If you see this after a fresh deploy, retrain and redeploy the ML stack — the fix is already in `ml/inference/serve.py`.

### SageMaker endpoint stuck in `Creating`

```bash
aws logs tail /aws/sagemaker/Endpoints/cloudsentinel-anomaly-detector --follow
```

### Frontend shows blank page after login

API calls are failing — the API Gateway URL in `frontend/.env` may be stale (it changes on every Compute stack redeploy). Get the latest URL:

```bash
aws cloudformation describe-stacks --stack-name CloudSentinel-Compute \
  --query "Stacks[0].Outputs[?contains(OutputKey,'ApiUrl')].OutputValue" --output text
```

Update `VITE_API_ENDPOINT` in `frontend/.env`, rebuild, and re-sync.

---

## Project Structure

```
cloudsentinel/
  app.py                    CDK entrypoint
  requirements.txt          CDK Python deps
  requirements-test.txt     Test deps (pytest)
  pytest.ini                pytest config — testpaths = tests
  cdk.json                  CDK config (region: us-east-1)
  docker-compose.yml        Local dev — serves frontend on localhost:3000
  stacks/
    network_stack.py        VPC (2 AZs, 1 NAT gateway)
    auth_stack.py           Cognito (tenantId custom JWT claim, admins group)
    storage_stack.py        DynamoDB tables + S3 data lake
    streaming_stack.py      Kinesis (2 shards, 24 h retention)
    compute_stack.py        Lambda + API Gateway
    ml_stack.py             SageMaker endpoint (Isolation Forest)
    alerting_stack.py       SNS topic + EventBridge bus
    frontend_stack.py       CloudFront + S3 (OAC)
  lambda/
    stream-processor/       Kinesis → SageMaker → DynamoDB → SNS
    api-handler/            All REST routes including /admin/*
  ml/
    training/train.py       Train Isolation Forest, upload model.tar.gz
    inference/serve.py      SageMaker script-mode inference
  frontend/
    Dockerfile              Multi-stage build → nginx
    nginx.conf              SPA routing + asset caching
    src/pages/
      Alerts.jsx            Anomaly alert table (per-tenant)
      Tenants.jsx           Account page (display name + plan)
      Ingest.jsx            Send test telemetry from browser
      Admin.jsx             Admin: manage tenants + cross-tenant alerts
  tests/
    test_stream_processor.py  24 unit tests — stream-processor Lambda
    test_api_handler.py       28 unit tests — api-handler Lambda
    test_serve.py             15 unit tests — ML inference script
  scripts/
    get_token.py            Fetch a Cognito JWT for the API
    send_telemetry.py       Stream real or simulated metrics to the pipeline
  docs/
    sending-telemetry.md    Guide for sending your machine's metrics
  .github/workflows/
    deploy.yml              Push to main → CDK deploy + S3 sync + CF invalidation
```

### Stack dependency order

```
Network ──┐
Auth    ──┤
Storage ──┼──▶ Streaming ──┐
          └──▶ ML          ├──▶ Compute ──▶ Frontend
               Alerting ───┘
```
