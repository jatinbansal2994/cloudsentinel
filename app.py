#!/usr/bin/env python3
"""
app.py — CloudSentinel CDK entrypoint.
Run: cdk deploy --all
"""
import aws_cdk as cdk

from stacks.network_stack   import NetworkStack
from stacks.auth_stack      import AuthStack
from stacks.storage_stack   import StorageStack
from stacks.streaming_stack import StreamingStack
from stacks.ml_stack        import MlStack
from stacks.compute_stack   import ComputeStack
from stacks.alerting_stack  import AlertingStack
from stacks.frontend_stack  import FrontendStack

app = cdk.App()

env = cdk.Environment(
    account=app.node.try_get_context("account"),
    region=app.node.try_get_context("region") or "us-east-1",
)

# ── Deploy stacks in dependency order ─────────────────────────────────────

network_stack   = NetworkStack(app,  "CloudSentinel-Network",   env=env)
auth_stack      = AuthStack(app,     "CloudSentinel-Auth",      env=env)
storage_stack   = StorageStack(app,  "CloudSentinel-Storage",   env=env)

streaming_stack = StreamingStack(
    app, "CloudSentinel-Streaming",
    tenant_table=storage_stack.tenant_table,
    env=env,
)

ml_stack = MlStack(
    app, "CloudSentinel-ML",
    data_bucket=storage_stack.data_bucket,
    env=env,
)

compute_stack = ComputeStack(
    app, "CloudSentinel-Compute",
    stream=streaming_stack.telemetry_stream,
    tenant_table=storage_stack.tenant_table,
    alert_table=storage_stack.alert_table,
    data_bucket=storage_stack.data_bucket,
    user_pool=auth_stack.user_pool,
    sagemaker_endpoint_name=ml_stack.endpoint_name,
    env=env,
)

alerting_stack = AlertingStack(
    app, "CloudSentinel-Alerting",
    alert_table=storage_stack.alert_table,
    env=env,
)

frontend_stack = FrontendStack(
    app, "CloudSentinel-Frontend",
    api=compute_stack.api,
    user_pool=auth_stack.user_pool,
    user_pool_client=auth_stack.user_pool_client,
    env=env,
)

# ── Tag every resource in every stack ─────────────────────────────────────
for stack in [network_stack, auth_stack, storage_stack, streaming_stack,
              ml_stack, compute_stack, alerting_stack, frontend_stack]:
    cdk.Tags.of(stack).add("Project",   "CloudSentinel")
    cdk.Tags.of(stack).add("ManagedBy", "CDK-Python")

app.synth()
