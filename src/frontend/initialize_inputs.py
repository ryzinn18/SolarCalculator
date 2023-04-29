from flask import flash
import boto3

import json
from typing import Callable

from src.utils.utils import post_item_to_dynamodb, DDB_RESOURCE, check_http_response, MONTHS_MAP


def validate(function: Callable) -> Callable:
    """Decorator function for handling exceptions when validating input data."""

    def wrapper_validate(*args, **kwargs):
        """Wraps function call in a try/except clause to catch FileNotFound, ValueError and general Exceptions"""
        try:
            function(*args, **kwargs)
        except TypeError:
            # Log error
            flash(
                "You submitted a blank value. Ensure no input fields are blank and rerun this tool.",
                category="error"
            )
            return False
        except ValueError:
            # Log error
            flash(
                "You entered an incorrect value. Ensure all inputs except Name and Address are numbers.",
                category="error"
            )
            return False
        else:
            return True

    return wrapper_validate


@validate
def _validate_energy_init_data(energy_data: list):
    """Validate that the data used to passed for initialization is correct."""

    for i in range(12):
        int(energy_data[i])


@validate
def _validate_energy_init_data(cost_data: list):
    """Validate that the data used to passed for initialization is correct."""

    for i in range(12):
        float(cost_data[i])


@validate
def _validate_rating_init_data(rating: str):
    """Validate that the data used to passed for initialization is correct."""

    float(rating)


@validate
def _validate_string_init_data(data: str):
    """Validate that the Name and Address fields are not null or NoneType."""
    if not data:
        raise TypeError


def validate_init_data(username: str, address: str, rating: str, energy_data: list, cost_data: list) -> bool:
    """Validate data passed & update data types in-place for mod_data & monthly_data."""
    name_validated = _validate_string_init_data(username)
    address_validated = _validate_string_init_data(address)
    rating_validated = _validate_rating_init_data(rating)
    energy_validated = _validate_energy_init_data(energy_data)
    cost_validated = _validate_energy_init_data(cost_data)

    return True if (name_validated and address_validated and rating_validated and energy_validated and cost_validated) \
        else False


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


def store_inputs(table_name: str, table_item: dict) -> dict:
    """Store input data to solarCalculatorTable-Inputs."""

    ddb_table = DDB_RESOURCE.Table(table_name)

    ddb_response = post_item_to_dynamodb(ddb_table, item=table_item)

    if not check_http_response(response_code=ddb_response):
        # Log warning
        print(f'\t{table_item["username"]}: Log warning')
        return {
            "status": {
                "status_code": 442,
                "message": "Could not write info to database."
            }
        }
    else:
        # Log info - success
        print(f'\t{table_item["username"]}: Log info - success')
        return {
            "status": {
                "status_code": 200,
                "message": "Data successfully written to database."
            }
        }


if __name__ == "__main__":
    # TEST STORE INPUTS
    # import threading
    # item2 = {
    #     "name": "TEST",
    #     "time_stamp": "123"
    #     "stage": "init",
    #     "address": "My Street 123",
    #     "state": "Ohio",
    #     "monthly_data": [1, 2, 1],
    #     "mod_data": {
    #         'mod_kwh': "0.4",
    #         "mod_price": "200"
    #     },
    #     "capacity": "14",
    # }
    # item1 = {
    #     "name": "TEST",
    #     "time_stamp": "123"
    #     "stage": "init",
    #     "address": "My Street 123",
    #     "state": "Ohio",
    #     "monthly_data": [1] * 1000,
    #     "mod_data": {
    #         'mod_kwh': "0.4",
    #         "mod_price": "200"
    #     },
    #     "capacity": "14",
    # }
    # print("creating threads")
    # t1 = threading.Thread(target=store_inputs, args=[item1])
    # t2 = threading.Thread(target=store_inputs, args=[item2])
    #
    # print("starting threads")
    # t1.start()
    # t2.start()

    # TEST SOLAR API CALL
    # inputs = {
    #     "name": "Ryan",
    #     "address": "123 My House, 93101",
    #     "capacity": 1
    # }
    # print(get_solar_data(inputs))

    # TEST VALIDATION
    # monthly = {
    #     "January": ["300", "300"],
    #     "February": ["100", "300"],
    #     "March": ["100", "300"],
    #     "April": ["100", "300"],
    #     "May": ["100", "300"],
    #     "June": ["100", "300"],
    #     "July": ["100", "300"],
    #     "August": ["100", "300"],
    #     "September": ["100", "300"],
    #     "October": ["100", "300"],
    #     "November": ["100", "300"],
    #     "December": ["100", "300"],
    # }
    # mod = {
    #     'mod_kwh': "0.4",
    #     "mod_price": "200"
    # }
    # print(
    #     validate_init_data(
    #         username="Ryan",
    #         address="123 Ocean Street",
    #         mod_data=mod,
    #         monthly_data=monthly
    #     )
    # )
    # print(type(mod['mod_price']))

    # TEST IN PLACE TRANSFORMATION
    # test = "0.3"
    # _validate_rating_init_data(test)
    # print(type(test))
    pass
