import json


def handler(event, _context):
    print(f'event={json.dumps(event)}')
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'body': f"Hello, CDK! You have hit {event.get('path', '<no path provided>')}"
    }
