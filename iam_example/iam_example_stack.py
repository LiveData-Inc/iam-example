from aws_cdk import Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from cdk_nag import NagSuppressions
from constructs import Construct


class IamExampleStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        policies = [
            iam.PolicyStatement(
                sid='IamExampleEventsActions',
                effect=iam.Effect.ALLOW,
                actions=[
                    'events:DisableRule',
                    'events:EnableRule',
                ],
                resources=[
                    self.format_arn(
                        service='events',
                        resource='rule',
                        resource_name='test_rule',
                    ),
                ]
            ),
        ]

        handler = lambda_.Function(
            self, "TestFunction",
            runtime=lambda_.Runtime.PYTHON_3_10,
            handler="hello.handler",
            code=lambda_.Code.from_asset("lambda_src"),
            reserved_concurrent_executions=10,  # HIPAA.Security-LambdaConcurrency
            initial_policy=policies
        )

        NagSuppressions.add_resource_suppressions(
            handler, [
                dict(
                    id='HIPAA.Security-LambdaDLQ',
                    reason='NOT AN ISSUE: suppressing for this demo'
                ),
                dict(
                    id='HIPAA.Security-LambdaInsideVPC',
                    reason='NOT AN ISSUE: suppressing for this demo'
                ),
            ]
        )
