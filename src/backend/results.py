# SolarCalculator/src/backend/results.py
# Integrates InputData and SolarPotentialData into Results data object and creates outputs
from pandas import DataFrame
from boto3 import resource as boto_resource
from pydantic import PositiveFloat

from csv import writer as csv_writer
from logging import getLogger
from decimal import Decimal
from json import loads as j_loads, dumps as j_dumps
from os import PathLike
from typing import Union, Sequence, Collection, Callable
import io
from concurrent.futures import ThreadPoolExecutor
import unittest

from utils import  MONTHS_MAP, IntListMonthly, FloatListMonthly, check_http_response, S3Url, invoke_lambda, import_json

LOGGER = getLogger(__name__)
S3 = boto_resource('s3')
DYNAMODB = boto_resource('dynamodb')


def _average(iterable: Union[Sequence, Collection]) -> int:
    """Calculate the average of the items in a Sequence/Collection as a rounded int value."""

    return round(sum(iterable) / len(iterable))


def get_data_df(
        input_data: dict, solar_potential_monthly: IntListMonthly, potential_cost_monthly: FloatListMonthly,
        potential_value: FloatListMonthly, savings_monthly: FloatListMonthly, cost_reduction_monthly: FloatListMonthly
) -> DataFrame:
    """Creates a pandas data frame with all the input, solar, and analysis data and their annual sums."""

    LOGGER.info('Creating DataFrame of core data')

    result = DataFrame(data={  # data type: [list monthly] + [annual total/annual average]
        'Month': list(MONTHS_MAP.values()) + ['Annual'],
        'Consumption kWh': input_data.get('consumption_monthly') + [input_data.get('consumption_annual')],
        'Cost $': input_data.get('cost_monthly') + [input_data.get('cost_annual')],
        'Potential kWh': solar_potential_monthly + [sum(solar_potential_monthly)],
        'Potential Value $': potential_value + [sum(potential_value)],
        'Potential Cost $': potential_cost_monthly + [sum(potential_cost_monthly)],
        'Savings $': savings_monthly + [sum(savings_monthly)],
        'Cost Reduction %': cost_reduction_monthly + [_average(cost_reduction_monthly)]
    })

    LOGGER.info(f'DataFrame successfully created: {result.to_dict()}')
    return result


def post_data_csv_to_s3(data_df: DataFrame, obj_key: str, bucket_name='sc-outputs-csv') -> S3Url.path:
    """Posts a DataFrame  as a csv to s3 bucket"""

    obj_key = obj_key + '.csv'
    # Create io buffer for csv
    csv_buffer = io.StringIO()
    data_df.to_csv(csv_buffer)
    # Post the object to dedicated bucket and return the http response
    S3.Bucket(bucket_name).put_object(Body=csv_buffer.getvalue(), Key=obj_key)
    # check_response(response=response['ResponseMetadata']['HTTPStatusCode'])

    return S3Url(bucket_name=bucket_name, obj_key=obj_key).path


def post_item_to_dynamodb(dynamo_table, item: dict) -> int:
    """Post a db item to DynamoDB and return the response code."""

    return dynamo_table.put_item(
        Item=item
    ).get('ResponseMetadata').get('HTTPStatusCode')


def _calculate_cost_per_kwh(cost: IntListMonthly, consumption: IntListMonthly) -> PositiveFloat:
    """Return the average cost per kWh for a year's inputs"""

    # Get a list of the cost/kWh for each month
    monthly_cost_per_kwh = [(cos / kwh) for cos, kwh in zip(cost, consumption)]
    # Calculate and return the average cost/kWh for the year
    return round(sum(monthly_cost_per_kwh) / len(monthly_cost_per_kwh), 2)


def calculate_production_insights(
        solar_potential_monthly: IntListMonthly, actual_consumption_monthly: IntListMonthly,
        cost_per_kwh: PositiveFloat, actual_cost_monthly: FloatListMonthly) -> dict:
    """Calculate insight into user inputs and solar data."""

    def _helper_calculate(func: Callable, zipped: tuple, arg3=None) -> FloatListMonthly:
        """Helper to clean up calculations for different monthly and annual figures."""

        out = []
        for arg1, arg2 in zipped:
            out.append(func(arg1, arg2, arg3))

        return out

    # Calculate Production Value, Potential Cost, Savings, and Cost Reduction
    production_value_monthly = _helper_calculate(
        func=lambda a1, a2, a3: round(a1 * a3, 2),
        zipped=zip(solar_potential_monthly, range(12)),
        arg3=cost_per_kwh
    )
    potential_cost_monthly = _helper_calculate(
        func=lambda a1, a2, a3: round((a1 - a2) * a3, 2),
        zipped=zip(actual_consumption_monthly, solar_potential_monthly),
        arg3=cost_per_kwh
    )
    cost_savings_monthly = _helper_calculate(
        func=lambda a1, a2, a3: round((a1 - a2), 2),
        zipped=zip(actual_cost_monthly, potential_cost_monthly)
    )
    cost_reduction_monthly = _helper_calculate(
        func=lambda a1, a2, a3: round(((a1 / a2) * 100), 2),
        zipped=zip(cost_savings_monthly, actual_cost_monthly)
    )
    energy_savings_monthly = _helper_calculate(
        func=lambda a1, a2, a3: round((a1 - a2), 2),
        zipped=zip(actual_consumption_monthly, solar_potential_monthly)
    )
    energy_reduction_monthly = _helper_calculate(
        func=lambda a1, a2, a3: round(((a1 / a2) * 100), 2),
        zipped=zip(energy_savings_monthly, actual_consumption_monthly)
    )

    return {
        'production_value_monthly': production_value_monthly,
        'production_value_annual': round(sum(production_value_monthly), 2),
        'potential_cost_monthly': potential_cost_monthly,
        'potential_cost_annual': round(sum(potential_cost_monthly), 2),
        'cost_savings_monthly': cost_savings_monthly,
        'cost_savings_annual': round(sum(cost_savings_monthly), 2),
        'cost_reduction_monthly': cost_reduction_monthly,
        'cost_reduction_annual': _average(cost_reduction_monthly),
        'energy_savings_monthly': energy_savings_monthly,
        'energy_savings_annual': round(sum(energy_savings_monthly), 2),
        'energy_reduction_monthly': energy_reduction_monthly,
        'energy_reduction_annual': _average(energy_reduction_monthly),
        'status': {
            'status_code': 200,
            'message': 'Monthly insights calculated successfully.'
        }
    }


def get_state_price(state: str) -> dict:
    """Query SolarCostData.json for price per watt in specific state."""
    try:
        data = import_json(
            path='/Users/ryanwright-zinniger/Desktop/SolarCalculator/src/frontend/static/data/SolarCostData.json'
        )
    except OSError:
        return {"status": {"status_code": 400, "message": f"Could not retrieve SolarCostData.json."}}

    try:
        state_price = round(float(data.get(state)), 2)
    except ValueError:
        return {"status": {"status_code": 400, "message": f"Could not retrieve data for state: '{state}'."}}

    return {
        "state_price": state_price,
        "status": {"status_code": 200, "message": "State price attained successfully."}
    }


def calculate_price_insights(state_price: float, capacity: float) -> dict:
    """Calculate price insight info and retrieve state price per watt."""

    try:
        total_price = round(state_price * capacity * 1000)
    except ValueError:
        return {"status": {
            "status_code": 400,
            "message": f"Encountered a value error with calculate_price_insights()."
        }}

    return {
        'total_price': total_price,
        'tax_credit': round(total_price * 0.3),
        'discount_price': round(total_price * 0.7),
        "status": {"status_code": 200, "message": "Price insights calculated successfully."}
    }


def get_results(input_data: dict) -> dict:
    """Create graphs, calculate savings and mod quantity, and return Results data object."""
    primary_key = f"{input_data['username']}-{input_data['time_stamp']}"

    LOGGER.info(f'Generating results for user: {primary_key}')

    cost_per_kwh = _calculate_cost_per_kwh(
        cost=input_data.get('cost_monthly'),
        consumption=input_data.get('consumption_monthly')
    )
    state_price = get_state_price(
        state=input_data.get('state')
    )
    production_insights = calculate_production_insights(
        solar_potential_monthly=input_data.get('output_monthly'),
        actual_consumption_monthly=input_data.get('consumption_monthly'),
        cost_per_kwh=cost_per_kwh,
        actual_cost_monthly=input_data.get('cost_monthly')
    )
    price_insights = calculate_price_insights(
        state_price=state_price.get('state_price'),
        capacity=input_data.get('capacity')
    )
    # Create DataFrame with all data for graphing/writing outputs
    production_df = get_data_df(
        input_data=input_data,
        solar_potential_monthly=input_data.get('output_monthly'),
        potential_cost_monthly=production_insights.get('potential_cost_monthly'),
        potential_value=production_insights.get('production_value_monthly'),
        savings_monthly=production_insights.get('savings_monthly'),
        cost_reduction_monthly=production_insights.get('cost_reduction_monthly'),
    )


    # Create graph inputs
    inputs_cost_graph = {
        "title": "Reported Cost vs Production Value",
        "df1": production_df['Cost $'].round(),
        "df2": production_df['Potential Value $'].round(),
        "label1": 'Reported Cost',
        "label2": 'Production Value',
        "y_label": 'Dollars',
        "graph_type": 'cost',
        "graph_flavor": "comparison",
        "uid": primary_key
    }
    inputs_energy_graph = {
        "title": "Energy Consumption vs Potential Production",
        "df1": production_df['Consumption kWh'],
        "df2": production_df['Potential kWh'],
        "label1": 'Energy Consumption',
        "label2": 'Potential Energy Production',
        "y_label": 'kWh',
        "graph_type": 'energy',
        "graph_flavor": "comparison",
        "uid": primary_key
    }
    with ThreadPoolExecutor() as executor:

        # Create data csv and save to s3 bucket
        url_data_csv = executor.submit(post_data_csv_to_s3, production_df, primary_key)

        # Create graphs and save to s3 buckets
        url_cost_graph = executor.submit(invoke_lambda, 'sc-be-results-graphs', inputs_cost_graph)
        url_energy_graph = executor.submit(invoke_lambda, 'sc-be-results-graphs', inputs_energy_graph)


    return {
        "url_data_csv": url_data_csv,
        "url_cost_graph": url_cost_graph,
        "url_energy_graph": url_energy_graph,
        "status": {
            "status_code": 200,
            "message": "Solar data retrieved successfully."
        }
    }

    # Create the Results data object
    # result = Results(
    #     uid=primary_key,
    #     name=input_data.get('name'),
    #     time_stamp=input_data.get('time_stamp'),
    #     status={
    #         "status_code": 200,
    #         "message": "get_results() called successfully."
    #     },
    #     address=input_data.get('address'),
    #     actual_consumption_monthly=input_data.get('consumption_monthly'),
    #     actual_cost_monthly=input_data.get('cost_monthly'),
    #     potential_production_monthly=input_data.get('output_monthly'),
    #     production_value=production_insights.get('production_value_monthly'),
    #     potential_cost_monthly=production_insights.get('potential_cost_monthly'),
    #     savings_monthly=production_insights.get('savings_monthly'),
    #     cost_reduction_monthly=production_insights.get('cost_reduction_monthly'),
    #     cost_reduction_average=_average(production_insights.get('cost_reduction_monthly')),
    #     results_data_json=results_df.to_json(),
    #     mod_quantity=input_data.get('mod_quantity'),
    #     url_data_csv=url_data_csv,
    #     url_graph_cost=url_cost_graph,
    #     url_graph_energy=url_energy_graph
    # )
    # LOGGER.info(f'Results data object successfully created and validated: {result}')
    #
    # # Declare which data will be included in table
    # table_item = {
    #     'uid': result.uid, 'name': result.name, 'address': result.address, 'mod_quantity': mod_quantity,
    #     'results_data': j_loads(j_dumps(results_df.to_json()), parse_float=Decimal),
    #     'data_csv': url_data_csv,
    #     'cost_graph': url_cost_graph,
    #     'energy_graph': url_energy_graph
    # }
    # # Post item to DynamoDB with necessary data and verify a non 200 response is given
    # response_code = post_item_to_dynamodb(dynamo_table=DYNAMODB.Table('sc-outputs'), item=table_item)
    # if not check_http_response(response_code=response_code):
    #     note = f"A {response_code} response was returned when writing to DynamoDB table 'sc-outputs'."
    #     LOGGER.error(note)
    #     raise Exception(note)
    #
    # LOGGER.info(
    #     f'Necessary data successfully written to DynamoDB table "sc-outputs" with key "{result.uid}"'
    # )
    # return result


def results_handler(event: dict, context) -> dict:
    """Handler function for getting final results event object."""

    LOGGER.info(f"Called sc-be-results's handler function for user: {event['username']}-{event['time_stamp']}")

    # Handle calling main function
    try:
        results_data = get_results(
            input_data=event,
        ).dict()
        LOGGER.info(f"sc-be-results's handler function successfully executed for user:"
                    f" {event['username']}-{event['time_stamp']}")
    except Exception as e:
        time_stamp = event.get("time_stamp") if event.get("time_stamp") else "NA"
        username = event.get("username") if event.get("username") else "NA"
        results_data = {
            "username": username,
            "time_stamp": time_stamp,
            "status": {
                "status_code": 400,
                "message": f"sc-be-results's handler function unsuccessfully executed for user: "
                           f"{event['username']}-{event['time_stamp']}.\n"
            }
        }
        LOGGER.error(e, exc_info=True)

    return results_data


class TestCostPerKwh(unittest.TestCase):
    def runTest(self):
        cost_per_kwh = _calculate_cost_per_kwh([2] * 12, [4] * 12)
        self.assertEqual(cost_per_kwh, 0.5)


if __name__ == '__main__':
    # from utils import import_json, SAMPLES
    #
    # print(
    #     results_handler(import_json(SAMPLES['event_ready_for_solar']), import_json(SAMPLES['event_ready_for_results'])))
    # unittest.main()
    print(_calculate_cost_per_kwh([2] * 12, [4] * 12))

def DEPRECATED_create_out_csv(header: dict, data_df: DataFrame, footer: dict, out_path: Union[PathLike, str]) -> None:
    """
    DEPRECATED: Could still be used at some point to allow users to download a csv all data.
    Create the output csv at the path passed.
    """
    """Original Call:
    # Create the output csv
    create_out_csv(
        header={'Name': input_data.get('name'),
                'Address': input_data.get('address'),
                'Cost/kWh': input_data.get('cost_per_kwh'),
                '': ''},  # Blank Row
        data_df=results_df,
        footer={'': '',  # Blank Row
                'Note:': solar_data.get('note'),
                'Potential kWh Source:': solar_data.get('source')},
        out_path=path_csv_out
    )"""

    LOGGER.info('Creating output csv')

    def _write_dict(to_write: dict) -> None:
        """Helper to iterate through a dict and write its items to csv."""

        for key, val in to_write.items():
            writer.writerow([key, val])

    with open(out_path, 'w') as out_file:
        writer = csv_writer(out_file, delimiter=',')
        # Write header data (Name, Address, Cost/kWh)
        _write_dict(to_write=header)
        # Write data (Cost, Actual Cost, Actual Consumption, etc.)
        data_df.to_csv(out_file, mode='a', index=False)
        # Write footer data (Notes & Sources)
        _write_dict(to_write=footer)

    LOGGER.info(f'Output csv successfully created: {out_path}')
