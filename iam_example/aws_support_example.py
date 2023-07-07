from aws_cdk import Stack, Aws
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kms as kms
from aws_cdk import aws_logs as logs
from aws_cdk import aws_lambda as lambda_
from cdk_nag import NagSuppressions
from constructs import Construct


class CustomNagStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        FUNCTION_NAME = 'My-Test-Function'

        #Key is necessary other wise Rule breaks > HIPAA.Security-CloudWatchLogGroupEncrypted: The CloudWatch Log Group is not encrypted with an AWS KMS key
        key = kms.Key(self, "Key",enable_key_rotation=True)
        key.grant_encrypt_decrypt(iam.ServicePrincipal(f'logs.{self.region}.amazonaws.com'))

        #Creating a Lambda Log Group beforehand.
        log_group = logs.LogGroup(self, "LogGroup",
            log_group_name=f'/aws/lambda/{FUNCTION_NAME}',
            encryption_key=key
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
                actions=['logs:CreateLogStream', 'logs:PutLogEvents'],
                resources=[log_group.log_group_arn]
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
            function_name=FUNCTION_NAME, #Explicitly function_name providing is necessary since we are separately creating a log group using the same name. 
            runtime=lambda_.Runtime.PYTHON_3_10,
            handler='hello.handler',
            code=lambda_.Code.from_asset('lambda_src'),
            reserved_concurrent_executions=10,  # HIPAA.Security-LambdaConcurrency
            role=lambda_role
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

