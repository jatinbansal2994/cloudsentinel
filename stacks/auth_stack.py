"""
stacks/auth_stack.py
Cognito User Pool for multi-tenant authentication.
Each user carries a tenantId custom attribute baked into their JWT.
Lambda reads this attribute to isolate data per tenant.
"""
import aws_cdk as cdk
from aws_cdk import aws_cognito as cognito
from constructs import Construct


class AuthStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # User pool — one shared pool for all tenants, isolated by tenantId attribute
        self.user_pool = cognito.UserPool(
            self, "TenantUserPool",
            user_pool_name="cloudsentinel-tenants",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_uppercase=True,
                require_digits=True,
                require_symbols=False,
            ),
            custom_attributes={
                # tenantId is immutable — set once at signup, lives in every JWT
                "tenantId": cognito.StringAttribute(mutable=False),
                # plan: free | pro | enterprise — can be updated
                "plan":     cognito.StringAttribute(mutable=True),
            },
            removal_policy=cdk.RemovalPolicy.DESTROY,  # change to RETAIN in prod
        )

        self.user_pool_client = self.user_pool.add_client(
            "WebClient",
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
            ),
        )

        cdk.CfnOutput(self, "UserPoolId",       value=self.user_pool.user_pool_id)
        cdk.CfnOutput(self, "UserPoolClientId", value=self.user_pool_client.user_pool_client_id)
