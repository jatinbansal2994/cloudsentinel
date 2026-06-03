"""
stacks/streaming_stack.py
Kinesis Data Stream for real-time telemetry ingestion.
2 shards = ~2 MB/s throughput. Add shards as tenant count grows.
24h retention = replay the last day of events if something breaks.
"""
import aws_cdk as cdk
from aws_cdk import aws_kinesis as kinesis, aws_dynamodb as dynamodb
from constructs import Construct


class StreamingStack(cdk.Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        tenant_table: dynamodb.Table,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.telemetry_stream = kinesis.Stream(
            self, "TelemetryStream",
            stream_name="cloudsentinel-telemetry",
            shard_count=2,                          # 1 shard ≈ 5 active tenants
            retention_period=cdk.Duration.hours(24),# replay buffer
            encryption=kinesis.StreamEncryption.MANAGED,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        cdk.CfnOutput(self, "StreamName", value=self.telemetry_stream.stream_name)
        cdk.CfnOutput(self, "StreamArn",  value=self.telemetry_stream.stream_arn)
