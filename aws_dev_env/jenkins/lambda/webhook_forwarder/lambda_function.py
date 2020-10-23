import os
from urllib import request, response

def lambda_handler(event, context):
    req = request.Request(
        os.environ['WEBHOOK_URL'],
        event["body"].encode('utf-8'),
        event["headers"]
    )
    resp = request.urlopen(req)
    html = resp.read()
    
    print(html)
    return {
        'statusCode': 200,
        'body': html
    }
