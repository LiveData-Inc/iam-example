from aws_cdk import Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kms as kms
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_logs as logs
from aws_cdk.aws_logs import RetentionDays
from cdk_nag import NagSuppressions
from constructs import Construct

FUNCTION_NAME = 'TestFunction'
NOT_AN_ISSUE = 'NOT AN ISSUE: suppressing for this demo'


class IamExampleStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Without this Key, we'd break this Rule:
        # HIPAA.Security-CloudWatchLogGroupEncrypted: The CloudWatch Log Group is not encrypted with an AWS KMS key
        key = kms.Key(self, 'TestKey', enable_key_rotation=True)
        key.grant_encrypt_decrypt(iam.ServicePrincipal(f'logs.{self.region}.amazonaws.com'))

        # Manually create our Lambda Function's CloudWatch Log Group
        log_group = logs.LogGroup(
            self, 'TestLogGroup',
            log_group_name=f'/aws/lambda/{FUNCTION_NAME}',
            encryption_key=key,
            retention=RetentionDays.SEVEN_YEARS
        )

        lambda_policy = iam.ManagedPolicy(
            self, 'LambdaManagedPolicy',
            description='Allow Lambda access to Log and Event',
            statements=[
                iam.PolicyStatement(
                    sid='IamExampleEventsActions',
                    effect=iam.Effect.ALLOW,
                    actions=['events:DisableRule', 'events:EnableRule'],
                    resources=[self.format_arn(service='events', resource='rule', resource_name='test_rule')]
                ),
                iam.PolicyStatement(
                    sid='IamExampleLambdaLogAccess',
                    effect=iam.Effect.ALLOW,
                    actions=['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
                    resources=[log_group.log_group_arn],
                )
            ]
        )
        lambda_role = iam.Role(
            self, 'LambdaRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[lambda_policy]
        )

        handler = lambda_.Function(
            self, 'TestFunction',
            # explicit function_name to match the above-created `log_group`
            function_name=FUNCTION_NAME,
            runtime=lambda_.Runtime.PYTHON_3_10,
            handler='hello.handler',
            code=lambda_.Code.from_asset('lambda_src'),
            reserved_concurrent_executions=10,  # HIPAA.Security-LambdaConcurrency
            role=lambda_role
        )

        lambda_policy.add_statements(
            iam.PolicyStatement(
                sid='IamExampleLambdaLogAccess',
                effect=iam.Effect.ALLOW,
                actions=['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
                resources=[handler.log_group.log_group_arn],
            )
        )

        NagSuppressions.add_resource_suppressions(
            handler, [
                dict(
                    id='HIPAA.Security-LambdaDLQ',
                    reason=NOT_AN_ISSUE
                ),
                dict(
                    id='HIPAA.Security-LambdaInsideVPC',
                    reason=NOT_AN_ISSUE
                ),
            ]
        )

        NagSuppressions.add_resource_suppressions(
            lambda_policy, [
                dict(
                    id='AwsSolutions-IAM5',
                    reason='Log Group requires wildcard permission for associated Log Streams'
                )
            ]
        )
