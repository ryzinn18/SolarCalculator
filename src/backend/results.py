# SolarCalculator/src/backend/results.py
# Integrates InputData and SolarPotentialData into Results data object and creates outputs
import matplotlib.pyplot as plt
from pandas import DataFrame
from boto3 import resource as boto_resource

from csv import writer as csv_writer
from logging import getLogger
from math import ceil
from decimal import Decimal
from json import loads as j_loads, dumps as j_dumps
from os import PathLike
from typing import Union, Sequence, Collection, Callable, Literal
import io
from datetime import datetime as dt

from utils import Results, MONTHS_MAP, IntListMonthly, FloatListMonthly, Status, check_http_response
from config import AWS_ACCESS_KEY, AWS_SECRET_KEY, DYNAMODB_TABLE_NAME

LOGGER = getLogger(__name__)
S3 = boto_resource('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
DYNAMODB = boto_resource('dynamodb', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)


class S3Url:
    __slots__ = 'path'

    def __init__(self, bucket_name: str, obj_key: str):
        """Simple class for creating specific s3 object paths."""

        self.path = f"https://{bucket_name}.s3.us-west-1.amazonaws.com/{obj_key.replace(':', '%')}"


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


def post_obj_to_s3(bucket_name: str, obj_key: str, content_type: str, obj_format='png') -> S3Url.path:
    """Posts an object (e.g., image) to s3 bucket."""

    obj_key = obj_key + '.' + obj_format
    # Create stream for the object
    data = io.BytesIO()
    plt.savefig(fname=data, format=obj_format, transparent=True)
    # Set stream position to start of stream
    data.seek(0)
    # Get bucket item, post the object, and return response
    bucket = S3.Bucket(bucket_name)
    bucket.put_object(Body=data, ContentType=content_type, Key=obj_key)

    return S3Url(bucket_name=bucket_name, obj_key=obj_key).path


def post_item_to_dynamodb(dynamo_table, item: dict) -> int:
    """Post a db item to DynamoDB and return the response code."""

    return dynamo_table.put_item(
        Item=item
    )['ResponseMetadata']['HTTPStatusCode']


def create_comparison_graph(
        title: str, df1: DataFrame, df2: DataFrame, label1: str, label2: str, y_label: str,
        graph_type: Literal['energy', 'cost'], uid: str) -> S3Url.path:
    """Creates a graph with 2 overlying plots for comparison."""

    LOGGER.info(f'Creating the {graph_type} comparison graph for uid "{uid}"')

    def _plot_bar(df: DataFrame, label: str, color: str, top: bool) -> None:
        """Plot a bar-plot and set the label."""
        opacity = 0.5 if top else 1
        # Plot the bar plot
        _ax = ax.bar(
            x=list(MONTHS_MAP.values()),
            height=df.drop(df.index[-1]),
            width=1,
            color=color,
            label=label,
            edgecolor='white',
            capstyle='round',
            alpha=opacity
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
        'cost': ['red', 'green']
    }
    # Set fonts as bold
    plt.title(weight='bold')
    plt.text(weight='bold')
    # Establish subplot figure.axes
    fig, ax = plt.subplots()
    ax.set_title(label=title)
    # Plot both datasets you are comparing as bar-plots
    _plot_bar(df=df1, label=label1, color=color_map[graph_type][0], top=False)
    _plot_bar(df=df2, label=label2, color=color_map[graph_type][1], top=True)
    # Set x and y labels
    ax.set_xlabel(xlabel='Month')
    ax.set_ylabel(ylabel=y_label)
    # Rotate month (x) labels by 45 degrees
    [item.set_rotation(45) for item in ax.get_xticklabels()]
    # Set background color
    ax.set_facecolor('lightseagreen')

    # Set legend
    legend = ax.legend(fontsize="large", loc='lower center')
    # legend.get_frame().set_color("xkcd:salmon")

    # Tighten layout
    plt.tight_layout()

    # Save the figure
    bucket_name = f"sc-outputs-graph-{graph_type}"
    url = post_obj_to_s3(
        bucket_name=bucket_name,
        obj_key='test' + uid,
        content_type='image/png'
    )

    LOGGER.info(f'Graph created and put in s3 bucket - {bucket_name} - with key "{uid}"')
    return url


def get_results(input_data: dict, solar_data: dict) -> Results:
    """Create graphs, calculate savings and mod quantity, and return Results data object."""

    LOGGER.info(f'Generating ResultsData for uid: {input_data.get("uid")}')

    def _helper_calculate(func: Callable, zipped: tuple, arg3=None) -> FloatListMonthly:
        """Helper to clean up calculations for different monthly and annual figures."""

        out = []
        for arg1, arg2 in zipped:
            out.append(func(arg1, arg2, arg3))

        return out

    # Calculate Production Value, Potential Cost, Savings, and Cost Reduction
    production_value = _helper_calculate(
        func=lambda a1, a2, a3: round(a1 * a3, 2),
        zipped=zip(solar_data.get('solar_potential_monthly'), range(12)),
        arg3=input_data.get("cost_per_kwh")
    )
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
        potential_value=production_value,
        savings_monthly=savings_monthly,
        cost_reduction_monthly=cost_reduction_monthly,
    )
    # Create data csv and save to s3 bucket
    url_data_csv = post_data_csv_to_s3(data_df=results_df, obj_key=input_data['uid'])
    # Create cost comparison graph
    url_cost_graph = create_comparison_graph(
        title="Reported Cost vs Production Value",
        df1=results_df['Cost $'].round(),
        df2=results_df['Potential Value $'].round(),
        label1='Reported Cost',
        label2='Production Value',
        y_label='Dollars',
        graph_type='cost',
        uid=input_data['uid']
    )
    # Create consumption vs production graph
    url_energy_graph = create_comparison_graph(
        title="Energy Consumption vs Potential Production",
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
        uid=input_data['uid'],
        name=input_data['name'],
        time_stamp=dt.now().__str__(),
        status=Status(status_code=200, message="get_results() called successfully."),
        address=input_data['address'],
        actual_consumption_monthly=input_data['consumption_monthly'],
        actual_cost_monthly=input_data['cost_monthly'],
        potential_production_monthly=solar_data['solar_potential_monthly'],
        production_value=production_value,
        potential_cost_monthly=potential_cost_monthly,
        savings_monthly=savings_monthly,
        cost_reduction_monthly=cost_reduction_monthly,
        cost_reduction_average=_average(cost_reduction_monthly),
        results_data_json=results_df.to_json(),
        mod_quantity=mod_quantity,
        url_data_csv=url_data_csv,
        url_graph_cost=url_cost_graph,
        url_graph_energy=url_energy_graph
    )
    LOGGER.info(f'Results data object successfully created and validated: {result}')

    # Declare which data will be included in table
    table_item = {
        'uid': result.uid, 'name': result.name, 'address': result.address, 'mod_quantity': mod_quantity,
        'results_data': j_loads(j_dumps(results_df.to_json()), parse_float=Decimal),
        'data_csv': url_data_csv,
        'cost_graph': url_cost_graph,
        'energy_graph': url_energy_graph
    }
    # Post item to DynamoDB with necessary data and verify a non 200 response is given
    response_code = post_item_to_dynamodb(dynamo_table=DYNAMODB.Table(DYNAMODB_TABLE_NAME), item=table_item)
    if not check_http_response(response_code=response_code):
        note = f"A {response_code} response was returned when writing to DynamoDB table '{DYNAMODB_TABLE_NAME}'."
        LOGGER.error(note)
        raise Exception(note)

    LOGGER.info(
        f'Necessary data successfully written to DynamoDB table "{DYNAMODB_TABLE_NAME}" with key "{result.uid}"'
    )
    return result


def results_handler(input_data: dict, solar_data: dict) -> dict:
    """Handler function for getting final results event object."""

    LOGGER.info(f'Called handler function for getting input data event for uid: {input_data["uid"]}')

    # Handle getting the necessary data
    try:
        results_data = get_results(
            input_data=input_data,
            solar_data=solar_data
        ).dict()
        LOGGER.info(f'Lambda Handler for results data successfully executed for uid: {input_data["uid"]}')
    except Exception as e:
        time_stamp = dt.now().__str__()
        uid = input_data.get("uid") if input_data.get("uid") else "NA" + time_stamp
        results_data = {
            "time_stamp": time_stamp,
            "uid": uid,
            "status": Status(
                status_code=400, message=f"get_results() called unsuccessfully due to error: {e.__repr__()}"
            )
        }
        LOGGER.error(e, exc_info=True)

    return results_data


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


if __name__ == '__main__':
    from utils import import_json, SAMPLES
    print(results_handler(import_json(SAMPLES['event_ready_for_solar']), import_json(SAMPLES['event_ready_for_results'])).get("status"))
