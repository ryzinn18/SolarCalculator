# SolarCalculator/src/utils.py
from pydantic import BaseModel, conlist, conint, PositiveInt, PositiveFloat
from boto3 import resource as boto_resource, client as boto_client

from typing import Union, Dict, Any, List, Type, TypeVar, Literal
from os.path import join
from pathlib import PurePath, Path

# from config import GOOGLE_API_SHEET_ID


DDB_RESOURCE = boto_resource('dynamodb')
DDB_CLIENT = boto_client('dynamodb')

JSON = Union[Dict[str, Any], List[Any], int, str, float, bool, Type[None]]
ROOT = Path(__file__).parents[1]

SAMPLES = {
    # 'sheet': GOOGLE_API_SHEET_ID,

    'csv_valid': join(ROOT, 'src/samples/consumption_valid.csv'),
    'csv_invalid': join(ROOT, 'src/samples/consumption_invalid.csv'),

    'xlsx_valid': join(ROOT, 'src/samples/consumption_valid.xlsx'),

    'input_valid': join(ROOT, 'src/samples/input_valid.json'),
    'input_invalid_type': join(ROOT, 'src/samples/input_invalid_type.json'),
    'input_invalid_value': join(ROOT, 'src/samples/input_invalid_value.json'),

    'event_valid_form': join(ROOT, 'samples/event_inputs/input_form.json'),
    'event_valid_csv': join(ROOT, 'src/samples/event_outputs/input_csv.json'),
    'event_valid_xlsx': join(ROOT, 'src/samples/event_inputs/input_xlsx.json'),
    'event_valid_sheet': join(ROOT, 'src/samples/event_inputs/input_sheet.json'),
    'event_ready_for_solar': join(ROOT, 'samples/event_inputs/ready_for_solar.json'),
    'event_ready_for_results': join(ROOT, 'samples/event_inputs/ready_for_results.json'),

    'solar_potential_valid': join(ROOT, 'samples/solar_potential_valid.json'),

    'results_valid': join(ROOT, 'src/samples/results_valid.json'),

    'out': PurePath(join(ROOT, 'src/OutputGraphs/RyanZinniger-SolarGraph.png')),
}

# Dictionary containing the month numbers (keys - int) and months spelled (values - str)
MONTHS_MAP = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}

# Custom types for pydantic objects and type-hinting
IntListMonthly = conlist(item_type=int, min_items=12, max_items=12)
FloatListMonthly = conlist(item_type=float, min_items=12, max_items=12)
AmbiguousListMonthly = conlist(item_type=float, min_items=12, max_items=12)
PandasDataFrame = TypeVar('PandasDataFrame')
StatusCode = conint(gt=99, lt=600)


def post_item_to_dynamodb(dynamo_table, item: dict) -> int:
    """Post a db item to DynamoDB and return the response code."""

    return dynamo_table.put_item(
        Item=item
    ).get('ResponseMetadata').get('HTTPStatusCode')


def get_item_from_dynamodb(ddb_name: str, key: dict) -> dict:
    """Get item from DynamoDB and return that item as dict."""

    ddb_table = DDB_RESOURCE.Table(ddb_name)
    response = ddb_table.get_item(
        Key=key
    )
    return response


def update_item_in_dynamodb(ddb_name: str, key: dict, update_expression: str, values: dict) -> int:
    """Update an item in DynamoDB, return the response code."""
    ddb_table = DDB_RESOURCE.Table(ddb_name)
    response = ddb_table.update_item(
        Key=key,
        UpdateExpression=update_expression,
        ExpressionAttributeValues=values,
        ReturnValues="UPDATED_NEW"
    )

    return response.get('ResponseMetadata').get('HTTPStatusCode')


def clean_name(name: str) -> str:
    """Remove all spaces and non-alphanumeric characters from name."""

    return ''.join(s for s in name if s.isalnum())


def check_http_response(response_code: int) -> bool:
    """Check if a response code is non 200 log an error if so, and return correct bool value."""

    if (not response_code) or (response_code < 200) or (response_code >= 300):
        return False
    else:
        return True


def import_json(path: str) -> dict:
    """
    Imports a .json file and returns that object as a json (dict)
    :param path: A relative path to the existing json file. Must include .json in the end of the string
    :return A json (dict) object
    """

    from os.path import isfile
    from json import load as j_load

    # Raise OSError if the .json does not exist
    if not isfile(path):
        raise OSError(
            f'The following path to a file does not exist:\n\t{path}'
        )
    # Raise OSError if the file path passed is not a .json
    if not path.endswith('.json'):
        raise OSError(
            f'The path provided is a file that is not a .json\n\t{path.split(r"/")[-1]}'
        )

    # Create the json object
    with open(path, 'r') as j:
        obj = j_load(j)

    return obj


def export_json(j_obj: JSON, target_directory: str, out_name: str) -> None:
    """Exports Pydantic model to json file in target_directory"""

    from os.path import isdir

    # Clean up variables passed
    target_directory = target_directory.rstrip(r'/')
    out_name = out_name.rstrip('.json')
    # Raise OSError if the target_directory does not exist
    if not isdir(target_directory):
        # LOGGER.error(f'The target directory specified does not exist: {target_directory}')
        raise OSError(
            f'The following target_directory does not exist:\n\t{target_directory}'
        )

    output = fr'{target_directory}/{out_name}.json'
    # Write the model passed to a .json at specified location
    with open(output, 'w') as out:
        out.write(j_obj)

    # LOGGER.info(f'The json file was successfully exported: {output}')


def delete_s3_obj(bucket_name: str, obj_key: str) -> int:
    """Delete an s3 object given bucket name and object's key and return the http response code."""

    from boto3 import resource as boto_resource

    s3 = boto_resource('s3')

    response = s3.Object(bucket_name, obj_key).delete()
    return response['ResponseMetadata']['HTTPStatusCode']


class Status(BaseModel):
    status_code: StatusCode
    message: str


class InputData(BaseModel):
    # Required
    uid: str
    name: str
    time_stamp: str
    status: Status
    address: str
    mod_kwh: PositiveFloat
    consumption_monthly: IntListMonthly
    consumption_annual: PositiveInt
    cost_monthly: FloatListMonthly
    cost_annual: PositiveFloat
    cost_per_kwh: PositiveFloat
    # Default
    units_consumption = "kiloWattHours"
    units_cost = "Dollars"
    sym_consumption = "kWh"
    sym_cost = "$"


class SolarPotentialData(BaseModel):
    # Required
    uid: str
    name: str
    time_stamp: str
    data_type: Literal['normal', 'actual']
    status: Status
    solar_potential_monthly: IntListMonthly
    solar_potential_annual: PositiveInt
    needed_kwh: PositiveInt
    mod_quantity: PositiveInt
    # Default
    units_solar_potential = "kiloWattHours"
    sym_solar_potential = "kWh"


class Results(BaseModel):
    # Required
    uid: str
    name: str
    time_stamp: str
    status: Status
    address: str
    actual_consumption_monthly: IntListMonthly
    actual_cost_monthly: FloatListMonthly
    potential_production_monthly: IntListMonthly
    production_value: FloatListMonthly
    potential_cost_monthly: AmbiguousListMonthly
    savings_monthly: FloatListMonthly
    cost_reduction_monthly: IntListMonthly
    cost_reduction_average: int
    mod_quantity: PositiveInt
    results_data_json: JSON
    url_data_csv: str
    url_graph_cost: str
    url_graph_energy: str


if __name__ == '__main__':
    print(get_item_from_dynamodb(ddb_name='solarCalculatorTable-Inputs', uid='DefaultDan-2023-04-28_11.10.05.641765'))
    pass
