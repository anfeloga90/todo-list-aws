import json
import decimalencoder
import todoList


def translate(event, context):
    # create a response
    item = todoList.get_item(event['pathParameters']['id'])
    translation = todoList.get_translation(item['text'], event['pathParameters']['language'])
    if translation:
        response = {
            "statusCode": 200,
            "body": json.dumps(translation, cls=decimalencoder.DecimalEncoder)
        }
    else:
        response = {
            "statusCode": 404,
            "body": ""
        }
    return response