"""
stacks/compute_stack.py
Lambda functions + API Gateway.

stream_processor: triggered by Kinesis → calls SageMaker → writes anomaly alerts → publishes SNS
api_handler:      handles REST requests from the React dashboard
"""
import aws_cdk as cdk
from aws_cdk import (
    aws_lambda as _lambda,
    aws_lambda_event_sources as event_sources,
    aws_apigateway as apigw,
    aws_kinesis as kinesis,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_cognito as cognito,
    aws_iam as iam,
    aws_sns as sns,
)
from constructs import Construct


class ComputeStack(cdk.Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        stream: kinesis.Stream,
        tenant_table: dynamodb.Table,
        alert_table: dynamodb.Table,
        data_bucket: s3.Bucket,
        user_pool: cognito.UserPool,
        sagemaker_endpoint_name: str,
        alert_topic: sns.Topic,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Shared environment variables injected into every Lambda
        shared_env = {
            "TENANT_TABLE":        tenant_table.table_name,
            "ALERT_TABLE":         alert_table.table_name,
            "DATA_BUCKET":         data_bucket.bucket_name,
            "SAGEMAKER_ENDPOINT":  sagemaker_endpoint_name,
            "KINESIS_STREAM_NAME": stream.stream_name,
            "ALERT_TOPIC_ARN":     alert_topic.topic_arn,
        }

        # ── Stream Processor Lambda ────────────────────────────────────────
        # Reads from Kinesis → scores via SageMaker → writes alerts → publishes SNS
        stream_processor = _lambda.Function(
            self, "StreamProcessor",
            function_name="cloudsentinel-stream-processor",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=_lambda.Code.from_asset("lambda/stream-processor"),
            timeout=cdk.Duration.minutes(5),
            memory_size=512,
            environment=shared_env,
        )

        # Kinesis trigger — fires when new records arrive in the stream
        stream_processor.add_event_source(
            event_sources.KinesisEventSource(
                stream,
                starting_position=_lambda.StartingPosition.LATEST,
                batch_size=100,              # process 100 events per invocation
                bisect_batch_on_error=True,  # isolate bad records on failure
            )
        )

        # Least-privilege permissions
        tenant_table.grant_read_data(stream_processor)
        alert_table.grant_write_data(stream_processor)
        data_bucket.grant_write(stream_processor)
        stream.grant_read(stream_processor)
        alert_topic.grant_publish(stream_processor)

        # Allow Lambda to call the SageMaker inference endpoint
        stream_processor.add_to_role_policy(
            iam.PolicyStatement(
                actions=["sagemaker:InvokeEndpoint"],
                resources=[
                    f"arn:aws:sagemaker:{self.region}:{self.account}"
                    f":endpoint/{sagemaker_endpoint_name}"
                ],
            )
        )

        # ── API Handler Lambda ─────────────────────────────────────────────
        # Handles REST requests from the React dashboard
        api_handler = _lambda.Function(
            self, "ApiHandler",
            function_name="cloudsentinel-api-handler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=_lambda.Code.from_asset("lambda/api-handler"),
            timeout=cdk.Duration.seconds(30),
            memory_size=256,
            environment=shared_env,
        )

        tenant_table.grant_read_write_data(api_handler)
        alert_table.grant_read_data(api_handler)
        stream.grant_write(api_handler)

        # ── API Gateway ────────────────────────────────────────────────────
        self.api = apigw.RestApi(
            self, "Api",
            rest_api_name="cloudsentinel-api",
            deploy_options=apigw.StageOptions(stage_name="v1"),
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
            ),
        )

        # Cognito authorizer — every request must carry a valid JWT
        authorizer = apigw.CognitoUserPoolsAuthorizer(
            self, "Authorizer",
            cognito_user_pools=[user_pool],
        )

        integration = apigw.LambdaIntegration(api_handler)

        # Routes — all protected by Cognito
        self.api.root.add_resource("ingest").add_method("POST", integration,
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=authorizer,
        )
        self.api.root.add_resource("alerts").add_method("GET", integration,
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=authorizer,
        )
        tenants = self.api.root.add_resource("tenants")
        tenants.add_method("GET",  integration,
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=authorizer,
        )
        tenants.add_method("POST", integration,
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=authorizer,
        )

        cdk.CfnOutput(self, "ApiUrl", value=self.api.url)
