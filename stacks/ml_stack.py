"""
CloudSentinel — ML Stack (Phase 3)
===================================
Deploys the Isolation Forest anomaly detector as a SageMaker real-time endpoint.

Prerequisites (run BEFORE cdk deploy):
    cd ml/training
    python train.py --bucket <CloudSentinelDataBucket>   # uploads model.tar.gz to S3

Stack outputs:
    CloudSentinelEndpointName  — consumed by compute_stack (Lambda env var)
    CloudSentinelSageMakerRoleArn
"""

from aws_cdk import (
    CfnOutput,
    Stack,
    aws_iam as iam,
    aws_sagemaker as sagemaker,
)
from constructs import Construct


# ---------------------------------------------------------------------------
# Built-in SageMaker sklearn container image URIs
# Source: https://github.com/aws/sagemaker-python-sdk/blob/master/src/sagemaker/image_uri_config/sklearn.json
# Version 1.2-1 matches the scikit-learn pin in ml/requirements.txt
# ---------------------------------------------------------------------------
_SKLEARN_IMAGES: dict[str, str] = {
    "us-east-1":      "683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3",
    "us-east-2":      "257758044811.dkr.ecr.us-east-2.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3",
    "us-west-1":      "746614075791.dkr.ecr.us-west-1.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3",
    "us-west-2":      "246618743249.dkr.ecr.us-west-2.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3",
    "ap-south-1":     "720646828776.dkr.ecr.ap-south-1.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3",
    "ap-southeast-1": "121021644041.dkr.ecr.ap-southeast-1.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3",
    "ap-southeast-2": "783357654285.dkr.ecr.ap-southeast-2.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3",
    "ap-northeast-1": "354813040037.dkr.ecr.ap-northeast-1.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3",
    "eu-west-1":      "141502667606.dkr.ecr.eu-west-1.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3",
    "eu-central-1":   "492215442770.dkr.ecr.eu-central-1.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3",
}

_MODEL_NAME          = "cloudsentinel-isolation-forest"
_ENDPOINT_CONFIG_NAME = "cloudsentinel-endpoint-config"
_ENDPOINT_NAME       = "cloudsentinel-anomaly-detector"
_MODEL_S3_PREFIX     = "cloudsentinel/models/model.tar.gz"


class MlStack(Stack):
    """
    Parameters
    ----------
    storage_bucket_name : str
        Name of the S3 bucket created by storage_stack (CloudSentinelDataBucket).
        The model.tar.gz must already be uploaded there before deploying this stack.
    region : str
        AWS region — used to select the correct sklearn container image URI.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        storage_bucket_name: str,
        region: str = "ap-south-1",
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ── SageMaker Execution Role ───────────────────────────────────────────
        self.sagemaker_role = iam.Role(
            self,
            "SageMakerExecutionRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            description="CloudSentinel - SageMaker execution role",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess"),
            ],
        )

        # Least-privilege S3 access — only the model bucket
        self.sagemaker_role.add_to_policy(
            iam.PolicyStatement(
                sid="ModelBucketAccess",
                actions=["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
                resources=[
                    f"arn:aws:s3:::{storage_bucket_name}",
                    f"arn:aws:s3:::{storage_bucket_name}/*",
                ],
            )
        )

        # ── Resolve container image URI ────────────────────────────────────────
        image_uri = _SKLEARN_IMAGES.get(region)
        if image_uri is None:
            raise ValueError(
                f"No sklearn container image URI defined for region {region!r}. "
                f"Add it to _SKLEARN_IMAGES in stacks/ml_stack.py."
            )

        model_s3_uri = f"s3://{storage_bucket_name}/{_MODEL_S3_PREFIX}"

        # ── SageMaker Model ────────────────────────────────────────────────────
        # model.tar.gz contains: model.pkl, scaler.pkl, metadata.json, serve.py
        # SAGEMAKER_PROGRAM tells the container which script handles inference.
        #
        # Explicit dependency on the role's inline S3 policy — without this,
        # CloudFormation creates the model in parallel with the policy attachment,
        # causing SageMaker to fail with an S3 access error on first deploy.
        self.cfn_model = sagemaker.CfnModel(
            self,
            "IsolationForestModel",
            execution_role_arn=self.sagemaker_role.role_arn,
            model_name=_MODEL_NAME,
            primary_container=sagemaker.CfnModel.ContainerDefinitionProperty(
                image=image_uri,
                model_data_url=model_s3_uri,
                environment={
                    "SAGEMAKER_PROGRAM":              "serve.py",
                    "SAGEMAKER_SUBMIT_DIRECTORY":     "/opt/ml/model/code",
                    "SAGEMAKER_CONTAINER_LOG_LEVEL":  "20",  # INFO
                    "SAGEMAKER_REGION":               region,
                },
            ),
        )

        # ── Endpoint Configuration ─────────────────────────────────────────────
        # ml.t2.medium: 2 vCPU, 4 GB RAM — adequate for Isolation Forest
        # Scale up to ml.m5.large if p99 latency > 100 ms under load
        self.cfn_endpoint_config = sagemaker.CfnEndpointConfig(
            self,
            "EndpointConfig",
            endpoint_config_name=_ENDPOINT_CONFIG_NAME,
            production_variants=[
                sagemaker.CfnEndpointConfig.ProductionVariantProperty(
                    model_name=self.cfn_model.model_name,  # type: ignore[arg-type]
                    variant_name="AllTraffic",
                    initial_instance_count=1,
                    instance_type="ml.t2.medium",
                    initial_variant_weight=1.0,
                )
            ],
        )
        # Wait for the inline S3 policy to be fully attached before model creation
        role_default_policy = self.sagemaker_role.node.find_child("DefaultPolicy")
        self.cfn_model.node.add_dependency(role_default_policy)

        self.cfn_endpoint_config.add_dependency(self.cfn_model)

        # ── Endpoint ───────────────────────────────────────────────────────────
        # Note: first deploy takes ~5–8 minutes while SageMaker pulls the image.
        self.cfn_endpoint = sagemaker.CfnEndpoint(
            self,
            "Endpoint",
            endpoint_name=_ENDPOINT_NAME,
            endpoint_config_name=self.cfn_endpoint_config.endpoint_config_name,  # type: ignore[arg-type]
        )
        self.cfn_endpoint.add_dependency(self.cfn_endpoint_config)

        # ── Expose for other stacks ────────────────────────────────────────────
        # compute_stack reads endpoint_name to set the Lambda env var
        self.endpoint_name: str = _ENDPOINT_NAME

        # ── CloudFormation Outputs ─────────────────────────────────────────────
        CfnOutput(
            self,
            "SageMakerEndpointName",
            value=_ENDPOINT_NAME,
            export_name="CloudSentinelEndpointName",
            description="SageMaker endpoint name — used by stream-processor Lambda",
        )
        CfnOutput(
            self,
            "SageMakerRoleArn",
            value=self.sagemaker_role.role_arn,
            export_name="CloudSentinelSageMakerRoleArn",
        )
        CfnOutput(
            self,
            "ModelS3Uri",
            value=model_s3_uri,
            description="S3 location of the packaged model artifact",
        )
