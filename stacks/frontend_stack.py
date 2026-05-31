"""
stacks/frontend_stack.py
S3 bucket for React build files + CloudFront CDN distribution.

After building the React app (npm run build in /frontend):
  aws s3 sync frontend/dist/ s3://<SiteBucketName>
CloudFront handles HTTPS, edge caching, and SPA routing (403 → index.html).
"""
import aws_cdk as cdk
from aws_cdk import (
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_apigateway as apigw,
    aws_cognito as cognito,
)
from constructs import Construct


class FrontendStack(cdk.Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        api: apigw.RestApi,
        user_pool: cognito.UserPool,
        user_pool_client: cognito.UserPoolClient,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 bucket — private, only CloudFront can read it
        site_bucket = s3.Bucket(
            self, "SiteBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        distribution = cloudfront.Distribution(
            self, "SiteDist",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(site_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
            ),
            default_root_object="index.html",
            error_responses=[
                # React SPA: any 403 from S3 means unknown route → serve index.html
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                )
            ],
        )

        cdk.CfnOutput(self, "CloudFrontUrl",   value=f"https://{distribution.distribution_domain_name}")
        cdk.CfnOutput(self, "SiteBucketName",  value=site_bucket.bucket_name)
        cdk.CfnOutput(self, "ApiEndpoint",      value=api.url)
        cdk.CfnOutput(self, "UserPoolId",       value=user_pool.user_pool_id)
        cdk.CfnOutput(self, "UserPoolClientId", value=user_pool_client.user_pool_client_id)
