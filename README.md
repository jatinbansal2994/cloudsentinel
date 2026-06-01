# CloudSentinel

Multi-tenant SaaS observability platform on AWS. Tenants push telemetry to a REST API → Kinesis buffers it → Lambda scores each event with an Isolation Forest on SageMaker → anomalies are stored in DynamoDB and published to SNS → a React dashboard shows live alerts per tenant.

## Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Deploy](#deploy)
- [Retraining the model](#retraining-the-model)
- [Teardown](#teardown)
- [Common Issues](#common-issues)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

---

## Architecture

```
Client / Tenant
      │
      ▼
API Gateway  (Cognito JWT auth)
      │
      ▼
Lambda: api-handler          ←── GET /alerts, GET|POST /tenants
      │  POST /ingest
      ▼
Kinesis Data Stream  (2 shards, 24 h retention)
      │
      ▼
Lambda: stream-processor
      ├── SageMaker endpoint  (Isolation Forest — anomaly score)
      ├── DynamoDB            (persist alert record)
      └── SNS topic           (fan-out notifications)
      
React Dashboard  (S3 + CloudFront)  ←── reads DynamoDB via api-handler
```

**Stack:** AWS CDK (Python 3.12) · Kinesis · Lambda · SageMaker (sklearn 1.2.1) · DynamoDB · Cognito · SNS · EventBridge · CloudFront

---

## Prerequisites

| Tool | Version | How to check |
|------|---------|--------------|
| Python 3.12 | CDK and Lambda runtime | `python3 --version` |
| Python 3.11 | ML training only (see note below) | `python3.11 --version` |
| Node.js | 18+ | `node --version` |
| AWS CLI | v2 | `aws --version` |
| AWS account | admin IAM permissions | `aws sts get-caller-identity` |

> **Why Python 3.11 for training?** The SageMaker built-in sklearn container runs sklearn 1.2.1. That version has no pre-built wheel for Python 3.12 and its Cython extensions are incompatible with Python 3.12's C API. A dedicated Python 3.11 training venv sidesteps this entirely — your CDK code still runs on Python 3.12.

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

```bash
aws configure
# Prompts for: Access Key ID · Secret Access Key · Region (us-east-1) · Output format (json)

# Verify
aws sts get-caller-identity
```

---

## Setup

### 1. Clone the repo

```bash
git clone git@github.com:jatinbansal2994/cloudsentinel.git
cd cloudsentinel
```

### 2. CDK virtual environment (Python 3.12)

```bash
python3 -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt
npm install                      # installs aws-cdk CLI into node_modules/
```

### 3. Bootstrap CDK

One-time per AWS account + region. Skip if already done by a teammate on the same account.

```bash
npx cdk bootstrap
```

### 4. ML training virtual environment (Python 3.11)

Used **only** to train the model. Keep this separate from the CDK venv.

```bash
python3.11 -m venv .venv-training
source .venv-training/bin/activate

pip install "numpy>=1.24,<2.0" scikit-learn==1.2.1 pandas boto3 joblib

# Confirm version matches SageMaker container
python3 -c "import sklearn; print(sklearn.__version__)"
# Expected: 1.2.1

deactivate
```

---

## Deploy

All commands run from the repo root. Switch venvs as indicated.

### Step 1 — Base infrastructure

```bash
source .venv/bin/activate
cdk deploy CloudSentinel-Network CloudSentinel-Auth CloudSentinel-Storage CloudSentinel-Streaming
```

Wait for all four stacks to reach `CREATE_COMPLETE` (~5 min total).

### Step 2 — Train and upload the model

The Storage stack must be deployed first — `train.py` auto-detects the S3 bucket from its CloudFormation output.

```bash
source .venv-training/bin/activate
cd ml/training
python3 train.py
# Trains Isolation Forest, packages model.tar.gz, uploads to S3
cd ../..
deactivate
```

### Step 3 — ML endpoint

```bash
source .venv/bin/activate
cdk deploy CloudSentinel-ML
```

SageMaker pulls the container image on first deploy — **allow 5–8 minutes**.

Confirm the endpoint is ready before proceeding:

```bash
aws sagemaker describe-endpoint \
  --endpoint-name cloudsentinel-anomaly-detector \
  --query "EndpointStatus" --output text
# Must return: InService
```

### Step 4 — Application stacks

```bash
cdk deploy CloudSentinel-Alerting CloudSentinel-Compute
```

### Step 5 — Verify

```bash
aws cloudformation list-stacks \
  --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE \
  --query "StackSummaries[?contains(StackName,'CloudSentinel')].{Name:StackName,Status:StackStatus}" \
  --output table
```

All 7 stacks should show `CREATE_COMPLETE`:

```
CloudSentinel-Network
CloudSentinel-Auth
CloudSentinel-Storage
CloudSentinel-Streaming
CloudSentinel-ML
CloudSentinel-Alerting
CloudSentinel-Compute
```

---

## Retraining the model

Run this whenever you change `ml/training/train.py` or `ml/inference/serve.py`:

```bash
source .venv-training/bin/activate
cd ml/training && python3 train.py && cd ../..
deactivate

source .venv/bin/activate
cdk deploy CloudSentinel-ML
```

---

## Teardown

```bash
source .venv/bin/activate
cdk destroy --all
```

> CloudFormation does not always delete the Kinesis stream on teardown. If a later `cdk deploy CloudSentinel-Streaming` fails with "already exists", delete the orphan manually:
> ```bash
> aws kinesis delete-stream --stream-name cloudsentinel-telemetry
> ```

---

## Common Issues

### `Resource already exists` — Kinesis stream

A previous deployment left the stream behind. Delete it and retry:

```bash
aws kinesis delete-stream --stream-name cloudsentinel-telemetry
cdk deploy CloudSentinel-Streaming
```

### `No module named 'distutils'` — installing sklearn

`.venv-training` was created with Python 3.12. sklearn 1.2.1 cannot be built on Python 3.12. Recreate it with Python 3.11:

```bash
rm -rf .venv-training
python3.11 -m venv .venv-training
source .venv-training/bin/activate
pip install "numpy>=1.24,<2.0" scikit-learn==1.2.1 pandas boto3 joblib
```

### `numpy.dtype size changed` — binary incompatibility

numpy 2.x was installed and is ABI-incompatible with sklearn 1.2.1 wheels. Downgrade numpy:

```bash
source .venv-training/bin/activate
pip install "numpy>=1.24,<2.0"
```

### `node array from the pickle has an incompatible dtype` — SageMaker ping fails

The model pickle was generated with a different sklearn version than the container (1.2.1). Retrain using `.venv-training` (Python 3.11, sklearn 1.2.1) and redeploy CloudSentinel-ML.

### SageMaker endpoint stuck in `Creating` for more than 15 min

Inspect the container logs directly:

```bash
aws logs tail /aws/sagemaker/Endpoints/cloudsentinel-anomaly-detector --follow
```

---

## Project Structure

```
cloudsentinel/
  app.py                    CDK entrypoint — defines all stacks and dependencies
  requirements.txt          CDK Python deps
  cdk.json                  CDK config (region: us-east-1)
  stacks/
    network_stack.py        VPC (2 AZs, 1 NAT gateway)
    auth_stack.py           Cognito user pool (tenantId custom JWT claim)
    storage_stack.py        DynamoDB tables + S3 data lake
    streaming_stack.py      Kinesis Data Stream (2 shards, 24 h retention)
    compute_stack.py        Lambda functions + API Gateway
    ml_stack.py             SageMaker endpoint (Isolation Forest)
    alerting_stack.py       SNS topic + EventBridge custom bus
    frontend_stack.py       CloudFront distribution + S3 origin (OAC)
  lambda/
    stream-processor/       Reads Kinesis → scores via SageMaker → writes DynamoDB → publishes SNS
    api-handler/            REST handlers: GET /alerts, GET|POST /tenants, POST /ingest
  ml/
    training/train.py       Trains Isolation Forest, builds model.tar.gz, uploads to S3
    inference/serve.py      SageMaker script-mode entry point (model_fn / predict_fn)
  docker/
    docker-compose.yml      Local dev stack (LocalStack + Redis + inference container)
```

### Stack deploy order

```
Network ──┐
Auth    ──┤
Storage ──┼──▶ Streaming ──┐
          └──▶ ML          ├──▶ Compute ──▶ Frontend
               Alerting ───┘
```
