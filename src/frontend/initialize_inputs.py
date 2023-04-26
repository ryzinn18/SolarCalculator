from flask import flash
import boto3

import json
from typing import Callable

from utils import post_item_to_dynamodb, DYNAMODB, check_http_response, MONTHS_MAP


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
def _validate_monthly_init_data(monthly_data: dict):
    """Validate that the data used to passed for initialization is correct."""

    for month in MONTHS_MAP.values():
        monthly_data[month] = [int(monthly_data[month][0]), float(monthly_data[month][1])]


@validate
def _validate_mod_init_data(mod_data: dict):
    """Validate that the data used to passed for initialization is correct."""

    mod_data['mod_kwh'] = float(mod_data['mod_kwh'])
    mod_data['mod_price'] = int(mod_data['mod_price'])


@validate
def _validate_string_init_data(data: str):
    """Validate that the Name and Address fields are not null or NoneType."""
    if data == "" or data is None:
        # Log Error
        raise TypeError


def validate_init_data(username: str, address: str, mod_data: dict, monthly_data: dict):
    """"""
    name_validated = _validate_string_init_data(username)
    address_validated = _validate_string_init_data(address)
    monthly_validated = _validate_monthly_init_data(monthly_data)
    mod_validated = _validate_mod_init_data(mod_data)

    return True if (name_validated and address_validated and monthly_validated and mod_validated) else False


def suggest_capacity(monthly_data: dict, annual_output: float) -> int:
    """Suggest solar array capacity (kwh) by dividing annual_consumption and annual_output"""
    annual_consumption = sum(data[0] for data in monthly_data.values())
    suggested_capacity = round(annual_consumption / annual_output)

    return suggested_capacity


def suggest_mod_quantity(capacity: int, mod_rating: float) -> int:
    """Suggest mod quantity by dividing capacity and mod_rating and rounding up."""

    return int(capacity // mod_rating) + 1


def get_solar_data(inputs: dict) -> dict:
    """Call Lambda function sc-be-solar for solar data."""
    lambda_client = boto3.client('lambda')

    response = lambda_client.invoke(
        FunctionName='sc-be-solar',
        InvocationType='RequestResponse',
        Payload=json.dumps(inputs)
    )
    if not check_http_response(response_code=response.get('ResponseMetadata').get('HTTPStatusCode')):
        # Log error
        flash("Something happened while processing your solar data! Please try again.", category="error")
        return {}

    return json.loads(response['Payload'].read().decode("utf-8"))


def store_inputs(
        username: str, time_stamp: str, address: str, monthly_data: dict, capacity: int, mod_data: dict) -> None:
    """Store input data to solarCalculatorTable-Inputs."""
    table_item = {
        "uid": f"{username}-{time_stamp}",
        "stage": "init" if capacity == 1 else "final",
        "name": username,
        "address": address,
        "monthly_data": monthly_data,
        "mod_data": mod_data,
        "capacity": capacity,
    }

    db_response = post_item_to_dynamodb(DYNAMODB.Table('solarCalculatorTable-Inputs'), item=table_item)

    if not check_http_response(response_code=db_response):
        # Log warning
        pass


if __name__ == "__main__":
    # TEST SOLAR API CALL
    # inputs = {
    #     "uid": "Ryan",
    #     "address": "123 My House",
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
    pass
