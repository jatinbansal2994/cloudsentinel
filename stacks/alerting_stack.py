"""
stacks/alerting_stack.py
SNS topic for email alerts + EventBridge custom bus for webhook dispatch.

When an anomaly is confirmed:
  Step Functions → SNS → email to tenant contacts
  Step Functions → EventBridge → webhook to tenant's own systems (Slack, PagerDuty...)
"""
import aws_cdk as cdk
from aws_cdk import aws_sns as sns, aws_events as events, aws_dynamodb as dynamodb
from constructs import Construct


class AlertingStack(cdk.Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        alert_table: dynamodb.Table,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.alert_topic = sns.Topic(
            self, "AlertTopic",
            topic_name="cloudsentinel-alerts",
            display_name="CloudSentinel Anomaly Alerts",
        )

        self.event_bus = events.EventBus(
            self, "WebhookBus",
            event_bus_name="cloudsentinel-webhooks",
        )

        cdk.CfnOutput(self, "AlertTopicArn", value=self.alert_topic.topic_arn)
        cdk.CfnOutput(self, "EventBusArn",   value=self.event_bus.event_bus_arn)
