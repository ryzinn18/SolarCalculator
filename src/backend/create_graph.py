from pandas import DataFrame
import matplotlib.pyplot as plt
from boto3 import resource as boto_resource

from logging import getLogger
from typing import Literal
import io

from utils import MONTHS_MAP, S3Url

LOGGER = getLogger(__name__)


def post_obj_to_s3(bucket_name: str, obj_key: str, content_type: str, obj_format='png') -> S3Url.path:
    """Posts an object (e.g., image) to s3 bucket."""

    LOGGER.info(f'Writing {obj_format} object to bucket "{bucket_name}" with key: "{obj_key}"')

    s3 = boto_resource('s3')
    obj_key = obj_key + '.' + obj_format
    # Create stream for the object
    data = io.BytesIO()
    plt.savefig(fname=data, format=obj_format, transparent=True)
    # Set stream position to start of stream
    data.seek(0)
    # Get bucket item, post the object, and return response
    bucket = s3.Bucket(bucket_name)
    bucket.put_object(Body=data, ContentType=content_type, Key=obj_key)

    LOGGER.info(f'Successfully wrote to bucket "{bucket_name}" with key: "{obj_key}"')

    return S3Url(bucket_name=bucket_name, obj_key=obj_key).path


def create_comparison_graph(
        title: str, df1: DataFrame, df2: DataFrame, label1: str, label2: str, y_label: str,
        graph_type: Literal['energy', 'cost'], uid: str) -> None:
    """Creates a graph with 2 overlying plots for comparison."""

    LOGGER.info(f'Creating the {graph_type} comparison graph for uid: "{uid}"')

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
    plt.title(label=title, weight='bold')
    plt.text(x=None, y=None, s=None, weight='bold')
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

    # # Save the figure
    # bucket_name = f"sc-outputs-graph-{graph_type}"
    # url = post_obj_to_s3(
    #     bucket_name=bucket_name,
    #     obj_key=uid,
    #     content_type='image/png'
    # )

    LOGGER.info(f'Graph formatted successfully')


def handle_graph(event, context):
    """"""
    flavor = event.get('graph_flavor')
    bucket_name = f"sc-outputs-graph-{event.get('graph_type')}"

    LOGGER.info(f'Lambda Handler invoked for {event.get("graph_type")}-{flavor} graph for user: {event.get("uid")}')

    if flavor == 'comparison':
        create_comparison_graph(
            title=event.get('title'),
            df1=event.get('df1'),
            df2=event.get('df2'),
            label1=event.get('label1'),
            label2=event.get('label2'),
            y_label=event.get('y_label'),
            graph_type=event.get('graph_type'),
            uid=event.get('uid')
        )

    url = post_obj_to_s3(
        bucket_name=bucket_name,
        obj_key=event.get('uid'),
        content_type='image/png'
    )

    LOGGER.info(f'Lambda Handler successfully invoked for user: {event.get("uid")}')

    return url





