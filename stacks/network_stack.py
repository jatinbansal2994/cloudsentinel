"""
stacks/network_stack.py
Creates the VPC that isolates all private resources.
Public subnets  → API Gateway / ALB
Private subnets → Lambda, ECS, ElastiCache
"""
import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class NetworkStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = ec2.Vpc(
            self, "CloudSentinelVpc",
            max_azs=2,          # 2 availability zones for high availability
            nat_gateways=1,     # 1 NAT gateway saves cost in dev; use 2 in prod
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,
                ),
            ],
        )

        cdk.CfnOutput(self, "VpcId", value=self.vpc.vpc_id)
