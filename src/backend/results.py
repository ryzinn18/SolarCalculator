# SolarCalculator/src/backend/results.py
# Integrates InputData and SolarPotentialData into Results data object and creates outputs
from csv import writer as csv_writer
from logging import getLogger
from math import ceil
from decimal import Decimal
from json import loads as j_loads, dumps as j_dumps
from os import PathLike
from typing import Union, Sequence, Collection, Callable, Literal
import io
import urllib

import matplotlib.pyplot as plt
from pandas import DataFrame
import boto3

from utils import Results, EventFinal, MONTHS_MAP, IntListMonthly, FloatListMonthly, import_json, SAMPLES
from config import aws_access_key, aws_secret_key, dynamodb_table_name

LOGGER = getLogger(__name__)
S3 = boto3.resource('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)


class S3Url:
    __slots__ = 'path'

    def __init__(self, bucket_name: str, obj_key: str, region_code="us-west-1"):
        """Simple class for creating specific s3 object paths."""

        self.path = f"s3://{bucket_name}/{obj_key}"


def _average(iterable: Union[Sequence, Collection]) -> int:
    """Calculate the average of the items in a Sequence/Collection as a rounded int value."""

    return round(sum(iterable) / len(iterable))


def get_data_df(
        input_data: dict, solar_potential_monthly: IntListMonthly, potential_cost_monthly: FloatListMonthly,
        savings_monthly: FloatListMonthly, cost_reduction_monthly: FloatListMonthly) -> DataFrame:
    """Creates a pandas data frame with all the input, solar, and analysis data and their annual sums."""

    LOGGER.info('Creating DataFrame of core data')

    result = DataFrame(data={  # data type: [list monthly] + [annual total/annual average]
        'Month': list(MONTHS_MAP.values()) + ['Annual'],
        'Consumption kWh': input_data.get('consumption_monthly') + [input_data.get('consumption_annual')],
        'Cost $': input_data.get('cost_monthly') + [input_data.get('cost_annual')],
        'Potential kWh': solar_potential_monthly + [sum(solar_potential_monthly)],
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
    # _check_response(response=response['ResponseMetadata']['HTTPStatusCode'], bucket_name=bucket_name, key=obj_key)

    return S3Url(bucket_name=bucket_name, obj_key=obj_key).path


def post_obj_to_s3(obj_format: Literal['png', 'csv'], bucket_name: str, obj_key: str, content_type: str) -> S3Url.path:
    """Posts an object (e.g., image) to s3 bucket"""

    obj_key = obj_key + '.png'
    # Create buffer for the object
    data = io.BytesIO()
    plt.savefig(fname=data, format=obj_format)
    data.seek(0)
    # Get bucket item, post the object, and return response
    bucket = S3.Bucket(bucket_name)
    bucket.put_object(Body=data, ContentType=content_type, Key=obj_key)
    # _check_response(response=response['ResponseMetadata']['HTTPStatusCode'], bucket_name=bucket_name, key=obj_key)

    return S3Url(bucket_name=bucket_name, obj_key=obj_key).path


def _check_response(response: int, bucket_name: str, key: str) -> None:
    """Check the response received from posting an object to an s3 bucket and Log/raise exception if not 200 response"""

    if not (200 >= response > 300):
        LOGGER.error(
            f'A {response} response was given when trying to post item with key "{key}" to s3 bucket "{bucket_name}"'
        )
        raise Exception(f'The item with key "{key}" was not posted to s3 bucket "{bucket_name}".')


def _delete_s3_obj(bucket_name: str, obj_key: str) -> int:
    """"""

    response = S3.Object(bucket_name, obj_key).delete()
    return response['ResponseMetadata']['HTTPStatusCode']


def create_comparison_graph(
        title: str, df1: DataFrame, df2: DataFrame, label1: str, label2: str, y_label: str,
        graph_type: Literal['energy', 'cost'], uid: str) -> S3Url.path:
    """Creates a graph with 2 overlying plots for comparison."""

    LOGGER.info(f'Creating the {graph_type} comparison graph for uid "{uid}"')

    def _plot_bar(df: DataFrame, label: str, color: str) -> None:
        """Plot a bar-plot and set the label."""

        # Plot the bar plot
        _ax = ax.bar(
            x=list(MONTHS_MAP.values()),
            height=df.drop(df.index[-1]),
            width=1,
            color=color,
            label=label,
            edgecolor='white',
            capstyle='round'
        )
        # Display the numbers on the bar-plots
        ax.bar_label(
            container=_ax,
            padding=-15,
            fmt='$%g' if graph_type == 'cost' else '%g'
        )

    # Define color_map for storing colors based on graph type
    color_map = {  # key: [df1-color, df2-color]
        'energy': ['indianred', 'gold'],
        'cost': ['lightcoral', 'darkolivegreen']
    }
    # Establish subplot figure.axes
    fig, ax = plt.subplots()
    ax.set_title(label=title)
    # Plot both datasets you are comparing as bar-plots
    _plot_bar(df=df1, label=label1, color=color_map[graph_type][0])
    _plot_bar(df=df2, label=label2, color=color_map[graph_type][1])
    # Set x and y labels
    ax.set_xlabel(xlabel='Month')
    ax.set_ylabel(ylabel=y_label)
    # Rotate month (x) labels by 45 degrees
    [item.set_rotation(45) for item in ax.get_xticklabels()]
    # Set background color
    ax.set_facecolor('lightseagreen')
    # Set legend
    legend = ax.legend(fontsize="large")
    # legend.get_frame().set_color("xkcd:salmon")

    # Tighten layout
    plt.tight_layout()

    # Save the figure
    bucket_name = f"sc-outputs-graph-{graph_type}"
    url = post_obj_to_s3(
        bucket_name=bucket_name,
        obj_format='png',
        obj_key='test' + uid,
        content_type='image/png'
    )

    LOGGER.info(f'Graph created and put in s3 bucket - {bucket_name} - with key "{uid}"')
    return url


def DEPRECATED_create_out_csv(header: dict, data_df: DataFrame, footer: dict, out_path: Union[PathLike, str]) -> None:
    """
    DEPRECATED: Could still be used at some point to allow users to download a csv all data so saving for now.
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


def get_results(input_data: dict, solar_data: dict) -> Results:
    """Create graphs, calculate savings and mod quantity, and return Results data object."""

    LOGGER.info(f'Generating ResultsData for uid: {input_data.get("uid")}')

    def _helper_calculate(func: Callable, zipped: tuple, arg3=None) -> FloatListMonthly:
        """Helper to clean up calculations for different monthly and annual figures."""

        out = []
        for arg1, arg2 in zipped:
            out.append(func(arg1, arg2, arg3))

        return out

    # Declare Dynamo DB table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(dynamodb_table_name)

    # Calculate Potential Cost, Savings, and Cost Reduction
    potential_cost_monthly = _helper_calculate(
        func=lambda a1, a2, a3: round((a1 - a2) * a3, 2),
        zipped=zip(input_data.get('consumption_monthly'), solar_data.get('solar_potential_monthly')),
        arg3=input_data.get('cost_per_kwh')
    )
    savings_monthly = _helper_calculate(
        func=lambda a1, a2, a3: round((a1 - a2), 2),
        zipped=zip(input_data.get('cost_monthly'), potential_cost_monthly)
    )
    cost_reduction_monthly = _helper_calculate(
        func=lambda a1, a2, a3: round(((a1 / a2) * 100), 2),
        zipped=zip(savings_monthly, input_data.get('cost_monthly'))
    )
    # Create DataFrame with all data for graphing/writing outputs
    results_df = get_data_df(
        input_data=input_data,
        solar_potential_monthly=solar_data.get('solar_potential_monthly'),
        potential_cost_monthly=potential_cost_monthly,
        savings_monthly=savings_monthly,
        cost_reduction_monthly=cost_reduction_monthly,
    )
    # Create data csv and save to s3 bucket
    url_data_csv = post_data_csv_to_s3(data_df=results_df, obj_key=input_data['uid'])
    # Create cost comparison graph
    url_cost_graph = create_comparison_graph(
        title=f"{input_data.get('name')}'s Actual vs Potential Cost",
        df1=results_df['Cost $'].round(),
        df2=results_df['Potential Cost $'].round(),
        label1='Actual Cost',
        label2='Potential Cost',
        y_label='Dollars',
        graph_type='cost',
        uid=input_data['uid']
    )
    # Create consumption vs production graph
    url_energy_graph = create_comparison_graph(
        title=f"{input_data.get('name')}'s Energy Consumption vs Production",
        df1=results_df['Consumption kWh'],
        df2=results_df['Potential kWh'],
        label1='Energy Consumption',
        label2='Potential Energy Production',
        y_label=solar_data.get('units_solar_potential'),
        graph_type='energy',
        uid=input_data['uid']
    )
    # Calculate amount of mods needed for project
    mod_quantity = ceil(solar_data.get('needed_kwh') / input_data.get('mod_kwh'))

    # Create the Results data object
    result = Results(
        uid=input_data.get('uid'),
        name=input_data.get('name'),
        address=input_data.get('address'),
        actual_consumption_monthly=input_data.get('consumption_monthly'),
        actual_cost_monthly=input_data.get('cost_monthly'),
        potential_production_monthly=solar_data.get('solar_potential_monthly'),
        potential_cost_monthly=potential_cost_monthly,
        savings_monthly=savings_monthly,
        cost_reduction_monthly=cost_reduction_monthly,
        cost_reduction_average=_average(cost_reduction_monthly),
        results_data_json=results_df.to_json(indent=4),
        mod_quantity=mod_quantity,
        uri_data_csv=url_data_csv,
        uri_graph_cost=url_cost_graph,
        uri_graph_energy=url_energy_graph
    )

    # item = j_loads(j_dumps(result.json()), parse_float=Decimal)
    response = table.put_item(
        Item={'uid': result.uid, 'name': result.name, 'address': result.address, 'mod_quantity': mod_quantity,
              'results_data': j_loads(j_dumps(results_df.to_json()), parse_float=Decimal),
              'data_csv': url_data_csv,
              'cost_graph': url_cost_graph,
              'energy_graph': url_energy_graph}
    )
    print(response['ResponseMetadata']['HTTPStatusCode'])

    LOGGER.info(f'Results data successfully created and validated: {result}')
    return result


def results_handler(event: dict, context) -> dict:
    """AWS Lambda Handler function for getting final results event object."""

    LOGGER.info(f'Called Lambda handler function for getting input data event for uid: {event["uid"]}')

    # Handle getting the necessary data
    input_data = event['input_data']
    solar_data = event['solar_data']
    results_data = get_results(
        input_data=input_data,
        solar_data=solar_data
    )
    out_event = EventFinal(
        uid=event['uid'],
        input_data=input_data,
        solar_data=solar_data,
        results_data=results_data
    )

    LOGGER.info(f'Lambda Handler for results data successfully executed for uid: {event["uid"]}')
    return out_event.dict()


if __name__ == '__main__':
    # print(delete_s3_obj(bucket_name='sc-outputs-graph-energy', obj_key="testRyan2023-02-15 00:55:15.142014"))
    # print(get_from_s3(bucket='sc-output-images', s3_file='testRyanCostGraph'))

    results_handler(import_json(SAMPLES['event_ready_for_results']), None)
    pass
