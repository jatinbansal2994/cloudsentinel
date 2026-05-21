"""
stacks/ml_stack.py
IAM role for SageMaker + endpoint name constant used by ComputeStack.

Actual training:  python ml/training/train.py
Actual deployment: python scripts/deploy_endpoint.py  (coming in Phase 3)
"""
import aws_cdk as cdk
from aws_cdk import aws_iam as iam, aws_s3 as s3
from constructs import Construct


class MlStack(cdk.Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        data_bucket: s3.Bucket,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # This is the endpoint name Lambda will call to score anomalies
        self.endpoint_name = "cloudsentinel-anomaly-detector"

        # SageMaker needs permission to read training data from S3
        # and to write model artifacts back to S3
        self.sagemaker_role = iam.Role(
            self, "SageMakerRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"),
            ],
        )

        data_bucket.grant_read_write(self.sagemaker_role)

        cdk.CfnOutput(self, "SageMakerRoleArn", value=self.sagemaker_role.role_arn)
        cdk.CfnOutput(self, "EndpointName",      value=self.endpoint_name)
