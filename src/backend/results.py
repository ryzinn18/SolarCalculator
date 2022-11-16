from backend.utils import MONTHS_MAP, IntListMonthly, FloatListMonthly
from backend.solar_potential import SolarPotentialData
from backend.input_handler import InputData
from os import PathLike, getcwd
from pathlib import PurePath
from math import ceil
import matplotlib.pyplot as plt
from pandas import DataFrame
from pydantic import BaseModel, PositiveInt, FilePath
from typing import Callable, Iterable, List


class Results(BaseModel):
    # Required
    name: str
    address: str
    potential_cost_monthly: FloatListMonthly
    potential_cost_annual: float
    savings_monthly: FloatListMonthly
    savings_annual: float
    cost_reduction_monthly: IntListMonthly
    cost_reduction_annual: int
    graph_path: FilePath
    mod_quantity: PositiveInt
    input_data: InputData
    solar_potential_data: SolarPotentialData


def _average(iterable: Iterable) -> int:
    """Helper function to calculate the average of the items in an iterable."""
    return round(sum(iterable) / len(iterable))


def create_comparison_graph(
        title: str, d1: DataFrame, d2: DataFrame, l1: str, l2: str, y_label: str, out_path: PathLike) -> None:
    """"""
    # Establish subplot figure.axes
    fig, ax = plt.subplots()
    ax.set_title(title=title, font_size='x-large')
    # Plot both datasets you are comparing as bar-plots
    ax1 = ax.bar(
        x=list(MONTHS_MAP.values()),
        height=d1,
        width=1,
        color='lightcoral',
        label=l1,
        edgecolor='black',
        capstyle='round'
    )
    ax2 = ax.bar(
        x=list(MONTHS_MAP.values()),
        height=d2,
        width=1,
        color='darkolivegreen',
        label=l2,
        edgecolor='black',
        capstyle='round'
    )
    # Display the numbers on the bar-plots
    ax.bar_label(
        container=ax1,
        padding=-15
    )
    ax.bar_label(
        container=ax2,
        padding=-15
    )
    # Set x and y labels
    ax.set_xlabel(xlabel='Month')
    [item.set_rotation(45) for item in ax.get_xticklabels()]
    ax.set_ylabel(ylabel=y_label)
    # Set background color
    ax.set_facecolor('teal')
    # Set legend
    legend = ax.legend(fontsize="large")
    # legend.get_frame().set_color("xkcd:salmon")
    # Tighten layout
    plt.tight_layout()
    # Save the figure
    plt.savefig(fname=out_path)


def create_solar_graph(input_data: InputData, solar_potential_data: SolarPotentialData,
                       out_relative_path: PathLike[str]) -> None:
    """Generate the Results graph."""
    potential = solar_potential_data.solar_potential_monthly
    consumption = input_data.consumption_monthly
    abv_months = list(map((lambda month: month[:3]), MONTHS_MAP.values()))

    fig, ax = plt.subplots()
    ax.set_title(f"{input_data.name}'s Consumption vs Production", fontsize="x-large")
    consumption_bar_plot = ax.bar(
        x=abv_months,
        height=consumption,
        width=1,
        color="orange",
        label="Consumption",
        edgecolor="black",
        capstyle='round'
    )
    ax.plot(
        abv_months, potential, "bo",
        label="Solar Potential",
        linestyle="--",
        linewidth=2,
        markersize=8
    )
    ax.bar_label(
        container=consumption_bar_plot,
        padding=-15
    )
    ax.set_ylabel(solar_potential_data.units_solar_potential)
    ax.set_xlabel('Month')
    ax.set_facecolor('C0')

    legend = ax.legend(fontsize="large")
    legend.get_frame().set_color("xkcd:salmon")
    plt.tight_layout()

    plt.savefig(fname=out_relative_path)


def create_cost_comparison_graph(data_df,
                                 out_relative_path):
    """"""
    fig, ax = plt.subplots()
    ax_actual = ax.bar(
        x=list(MONTHS_MAP.values()),
        height=data_df['Cost $'],
        color='lightcoral',
        label='Actual Cost'
    )
    ax_potential = ax.bar(
        x=list(MONTHS_MAP.values()),
        height=list(data_df['Potential Cost $'].values),
        color='darkolivegreen',
        label='Potential Cost'
    )
    ax.bar_label(
        container=ax_actual,
        padding=-15
    )
    ax.bar_label(
        container=ax_potential,
        padding=-15
    )
    ax.set_xlabel('Month')
    for item in ax.get_xticklabels():
        item.set_rotation(45)

    ax.set_ylabel('Cost')

    ax.set_facecolor('teal')
    ax.legend()
    fig = ax.get_figure()
    fig.savefig(out_relative_path)


def get_data_df(
        input_data: InputData, solar_potential_monthly: IntListMonthly, potential_cost_monthly: FloatListMonthly,
        savings_monthly: FloatListMonthly, cost_reduction_monthly: FloatListMonthly) -> DataFrame:
    """Creates a pandas data from with all the input, solar, and analysis data."""
    return DataFrame(
        data={'Month': list(MONTHS_MAP.values()) + ['Annual'],
              'Consumption kWh': input_data.consumption_monthly + [input_data.consumption_annual],
              'Cost $': input_data.cost_monthly + [input_data.cost_annual],
              'Potential kWh': solar_potential_monthly + [sum(solar_potential_monthly)],
              'Potential Cost $': potential_cost_monthly + [sum(potential_cost_monthly)],
              'Savings $': savings_monthly + [sum(savings_monthly)],
              'Cost Reduction %': cost_reduction_monthly + [_average(cost_reduction_monthly)]},
    )


def create_out_csv(header: dict, data_df: DataFrame, out_relative_path: PathLike[str]) -> None:
    """Creates the output csv at the relative path passed."""
    from csv import DictWriter

    with open(out_relative_path, 'w') as out_file:
        writer = DictWriter(out_file, fieldnames=['Name', header['Name']])

        for key, val in header.items():
            writer.writerow({'Name': key, header['Name']: val})

        data_df.to_csv(out_file, mode='a')


def get_results(input_data: InputData, solar_potential_data: SolarPotentialData) -> Results:
    """Get graph, calculate your savings and mod quantity, and return your data objects."""

    def _helper_calculate(func: Callable, zipped: tuple, arg3=None) -> FloatListMonthly:
        """Helper to clean up calculations for different monthly and annual figures."""
        out = []
        for arg1, arg2 in zipped:
            out.append(func(arg1, arg2, arg3))

        return out

    path_solar_graph = PurePath(fr"./OutputGraphs/{input_data.name}-SolarGraph.png")
    path_cost_graph = PurePath(fr"./OutputGraphs/{input_data.name}-CostGraph.png")
    path_out_csv = PurePath(fr"./OutputDataFiles/{input_data.name}-OutputData.csv")

    """create_solar_graph(
        input_data=input_data,
        solar_potential_data=solar_potential_data,
        out_relative_path=path_solar_graph
    )"""

    potential_cost_monthly = _helper_calculate(
        func=lambda a1, a2, a3: round((a1 - a2) * a3, 2),
        zipped=zip(input_data.consumption_monthly, solar_potential_data.solar_potential_monthly),
        arg3=input_data.cost_per_kwh
    )

    savings_monthly = _helper_calculate(
        func=lambda a1, a2, a3: round((a1 - a2), 2),
        zipped=zip(input_data.cost_monthly, potential_cost_monthly)
    )
    cost_reduction_monthly = _helper_calculate(
        func=lambda a1, a2, a3: round((a1 / a2), 2),
        zipped=zip(potential_cost_monthly, input_data.consumption_monthly)
    )
    data_df = get_data_df(
        input_data=input_data,
        solar_potential_monthly=solar_potential_data.solar_potential_monthly,
        potential_cost_monthly=potential_cost_monthly,
        savings_monthly=savings_monthly,
        cost_reduction_monthly=cost_reduction_monthly,
    )
    """create_cost_comparison_graph(
        data_df=data_df.drop(data_df.index[-1]),
        out_relative_path=path_cost_graph
    )"""
    create_comparison_graph(
        title=f"{input_data.name}'s Actual Cost vs Potential Cost",
        d1=data_df['Cost $'],
        d2=data_df['Potential Cost $'],
        l1='Actual Cost',
        l2='Potential Cost',
        y_label='Dollars',
        out_path=path_cost_graph
    )
    create_comparison_graph(
        title=f"{input_data.name}'s Consumption vs Production",
        d1=data_df['Consumption kWh'],
        d2=data_df['Potential kWh'],
        l1='Energy Consumption',
        l2='Potential Energy Production',
        y_label=solar_potential_data.units_solar_potential,
        out_path=path_solar_graph
    )
    """create_out_csv(
        header={'Name': input_data.name,
                'Address': input_data.address,
                'Cost/kWh': input_data.cost_per_kwh,
                '': ''},  # Blank Row
        data_df=data_df,
        out_relative_path=relative_csv_path
    )"""

    """return Results(
        name=input_data.name,
        address=input_data.address,
        potential_cost_monthly=potential_cost_monthly,
        potential_cost_annual=sum(potential_cost_monthly),
        savings_monthly=savings_monthly,
        savings_annual=sum(savings_monthly),
        cost_reduction_monthly=cost_reduction_monthly,
        cost_reduction_annual=_average(cost_reduction_monthly),
        graph_path=graph_path,
        mod_quantity=ceil(solar_potential_data.needed_kwh / input_data.mod_kwh),
        input_data=input_data,
        solar_potential_data=solar_potential_data
    )"""


if __name__ == '__main__':
    pass
