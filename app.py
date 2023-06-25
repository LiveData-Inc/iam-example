#!/usr/bin/env python3
import os

import aws_cdk as cdk
from cdk_nag import AwsSolutionsChecks, HIPAASecurityChecks, NagSuppressions

from iam_example.iam_example_stack import IamExampleStack

app = cdk.App()
stack = IamExampleStack(
    app, "IamExampleStack",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

cdk.Aspects.of(app).add(AwsSolutionsChecks())
cdk.Aspects.of(app).add(HIPAASecurityChecks())

NagSuppressions.add_stack_suppressions(
    stack, [
        dict(
            id='AwsSolutions-IAM4',
            reason='TODO: replace managed policies'
        ),
        dict(
            id='HIPAA.Security-IAMNoInlinePolicy',
            reason='TODO: replace'
        ),
    ]
)

app.synth()
