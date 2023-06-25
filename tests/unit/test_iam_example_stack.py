import aws_cdk as core
import aws_cdk.assertions as assertions

from iam_example.iam_example_stack import IamExampleStack


def test_lambda_created():
    app = core.App()
    stack = IamExampleStack(app, "iam-example")
    template = assertions.Template.from_stack(stack)
    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "hello.handler"
    })
