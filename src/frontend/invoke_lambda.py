import boto3
from flask import flash

import json

from src.utils.utils import check_http_response


def get_solar_data(solar_inputs: dict) -> dict:
    """Call Lambda function sc-be-solar for solar data."""
    lambda_client = boto3.client('lambda')

    response = lambda_client.invoke(
        FunctionName='sc-be-solar',
        InvocationType='RequestResponse',
        Payload=json.dumps(solar_inputs)
    )
    outputs = json.loads(response['Payload'].read().decode("utf-8"))

    response_status = response.get('ResponseMetadata').get('HTTPStatusCode')
    response_outputs = outputs.get('status').get('status_code')
    if not check_http_response(response_status) or not check_http_response(response_outputs):
        if response_outputs == 422:
            # Log error - PvWatts call failed
            flash(f"{outputs.get('errors')[0]}. If errors persist, just enter your Zip Code.", category="error")
        else:
            # Log error - Lambda invoke failed/PvWatts call failed
            flash("Something happened while processing your solar data! Please try again.", category="error")

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