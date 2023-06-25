from aws_cdk import Stack
from aws_cdk import aws_lambda as lambda_
from cdk_nag import NagSuppressions
from constructs import Construct


class IamExampleStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        handler = lambda_.Function(
            self, "TestFunction",
            runtime=lambda_.Runtime.PYTHON_3_10,
            handler="hello.handler",
            code=lambda_.Code.from_asset("lambda_src"),
            reserved_concurrent_executions=10,  # HIPAA.Security-LambdaConcurrency
        )

        NagSuppressions.add_resource_suppressions(
            handler, [
                dict(
                    id='HIPAA.Security-LambdaDLQ',
                    reason='suppressing for this demo'
                ),
                dict(
                    id='HIPAA.Security-LambdaInsideVPC',
                    reason='suppressing for this demo'
                )
            ]
        )
