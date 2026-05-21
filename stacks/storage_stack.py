"""
stacks/storage_stack.py
DynamoDB tables + S3 data lake.
PAY_PER_REQUEST billing = auto-scales to any traffic with no capacity planning.
"""
import aws_cdk as cdk
from aws_cdk import aws_dynamodb as dynamodb, aws_s3 as s3
from constructs import Construct


class StorageStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ── Tenant config table ────────────────────────────────────────────
        # Stores: tenant profile, alert thresholds, plan info
        # PK: tenantId | SK: CONFIG / RULE#<ruleId>
        self.tenant_table = dynamodb.Table(
            self, "TenantTable",
            table_name="cloudsentinel-tenants",
            partition_key=dynamodb.Attribute(
                name="tenantId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="sk", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            time_to_live_attribute="ttl",
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # ── Anomaly alerts table ───────────────────────────────────────────
        # Stores: every anomaly detected per tenant
        # PK: tenantId | SK: alertId (UUID)
        self.alert_table = dynamodb.Table(
            self, "AlertTable",
            table_name="cloudsentinel-alerts",
            partition_key=dynamodb.Attribute(
                name="tenantId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="alertId", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            time_to_live_attribute="ttl",   # auto-delete after 7 days
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # GSI: query alerts by severity (critical / warning) within a tenant
        self.alert_table.add_global_secondary_index(
            index_name="severity-index",
            partition_key=dynamodb.Attribute(
                name="tenantId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="severity", type=dynamodb.AttributeType.STRING
            ),
        )

        # ── S3 data lake ───────────────────────────────────────────────────
        # Kinesis Firehose streams raw telemetry here.
        # Athena can query it with SQL — no servers needed.
        self.data_bucket = s3.Bucket(
            self, "DataLake",
            bucket_name=f"cloudsentinel-datalake-{self.account}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="move-to-ia",
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=cdk.Duration.days(30),
                        )
                    ],
                )
            ],
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        cdk.CfnOutput(self, "DataBucketName", value=self.data_bucket.bucket_name)
