from lambda_src.hello import handler


def test_handler():
    response = handler({'path': '/test/path'}, object())
    assert '/test/path' in response['body']
