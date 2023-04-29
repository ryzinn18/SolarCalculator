from boto3 import client as boto_client

import json

from src.utils.utils import check_http_response


def invoke_lambda(function: str, inputs: dict) -> dict:
    """Call Lambda function sc-be-solar for solar data."""
    lambda_client = boto_client('lambda')

    response = lambda_client.invoke(
        FunctionName=function,
        InvocationType='RequestResponse',
        Payload=json.dumps(inputs)
    )
    outputs = json.loads(response.get('Payload').read().decode("utf-8"))

    response_status = response.get('ResponseMetadata').get('HTTPStatusCode')
    response_outputs = outputs.get('status').get('status_code')
    if not check_http_response(response_status) or not check_http_response(response_outputs):
        if response_outputs == 422:
            # Log error - PvWatts call failed
            pass
        else:
            # Log error - Lambda invoke failed/PvWatts call failed
            pass

        return {}

    return outputs


if __name__ == '__main__':
    # TEST SOLAR API CALL
    # inputs = {
    #     "name": "Ryan",
    #     "address": "123 My House, 93101",
    #     "capacity": 1
    # }
    # print(get_solar_data(inputs))
    pass