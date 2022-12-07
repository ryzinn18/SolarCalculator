# ~/src/backend/results.py
from utils import get_root
from backend.utils import MONTHS_MAP, IntListMonthly, FloatListMonthly, AmbiguousListMonthly, \
    PandasDataFrame, LOGGER
from backend.solar_potential import SolarPotentialData
from backend.inputs import InputData
from csv import writer as csv_writer
from os import PathLike
from pathlib import PurePath
from math import ceil
import matplotlib.pyplot as plt
from pandas import DataFrame
from pydantic import BaseModel, PositiveInt, FilePath
from typing import Callable, Iterable, Literal


class Results(BaseModel):
    # Required
    name: str
    address: str
    actual_consumption_monthly: IntListMonthly
    actual_cost_monthly: FloatListMonthly
    potential_production_monthly: IntListMonthly
    potential_cost_monthly: AmbiguousListMonthly
    savings_monthly: FloatListMonthly
    cost_reduction_monthly: IntListMonthly
    energy_graph_path: FilePath
    cost_graph_path: FilePath
    results_data_frame: PandasDataFrame
    results_csv_path: FilePath
    mod_quantity: PositiveInt
    input_data: InputData
    solar_potential_data: SolarPotentialData


def _average(iterable: Iterable) -> int:
    """Helper function to calculate the average of the items in an iterable."""
    return round(sum(iterable) / len(iterable))


def create_comparison_graph(
        title: str, d1: DataFrame, d2: DataFrame, l1: str, l2: str, y_label: str,
        out_path: PathLike, graph_type: Literal['energy', 'cost']) -> None:
    """Creates a graph with 2 overlying plots for comparison."""
    LOGGER.info(f'Creating the comparison graph titled: {title}')

    def _plot_bar(d: DataFrame, l: str, color: str) -> None:
        """Helper function to plot each bar-plot and set the label"""
        _ax = ax.bar(
            x=list(MONTHS_MAP.values()),
            height=d.drop(d.index[-1]),
            width=1,
            color=color,
            label=l,
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
    color_map = {  # key: [d1-color, d2-color]
        'energy': ['indianred', 'gold'],
        'cost': ['lightcoral', 'darkolivegreen']
    }
    # Establish subplot figure.axes
    fig, ax = plt.subplots()
    ax.set_title(label=title)
    # Plot both datasets you are comparing as bar-plots
    _plot_bar(d=d1, l=l1, color=color_map[graph_type][0])
    _plot_bar(d=d2, l=l2, color=color_map[graph_type][1])
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
    plt.savefig(fname=out_path)

    LOGGER.info(f'Graph created: {out_path}')


def get_data_df(
        input_data: InputData, solar_potential_monthly: IntListMonthly, potential_cost_monthly: FloatListMonthly,
        savings_monthly: FloatListMonthly, cost_reduction_monthly: FloatListMonthly) -> DataFrame:
    """Creates a pandas data from with all the input, solar, and analysis data."""
    LOGGER.info('Creating DataFrame of core data')
    result = DataFrame(data={
        'Month': list(MONTHS_MAP.values()) + ['Annual'],
        'Consumption kWh': input_data.consumption_monthly + [input_data.consumption_annual],
        'Cost $': input_data.cost_monthly + [input_data.cost_annual],
        'Potential kWh': solar_potential_monthly + [sum(solar_potential_monthly)],
        'Potential Cost $': potential_cost_monthly + [sum(potential_cost_monthly)],
        'Savings $': savings_monthly + [sum(savings_monthly)],
        'Cost Reduction %': cost_reduction_monthly + [_average(cost_reduction_monthly)]
        })

    LOGGER.info('DataFrame successfully created')
    return result


def create_out_csv(header: dict, data_df: DataFrame, footer: dict,
                   out_relative_path: PathLike[str]) -> None:
    """Creates the output csv at the relative path passed."""
    LOGGER.info('Creating output csv')

    def _write_dict(to_write: dict) -> None:
        """Helper to iterate through a dict and write its items to csv."""
        for key, val in to_write.items():
            writer.writerow([key, val])

    with open(out_relative_path, 'w') as out_file:
        writer = csv_writer(out_file, delimiter=',')

        _write_dict(to_write=header)

        data_df.to_csv(out_file, mode='a', index=False)

        _write_dict(to_write=footer)

    LOGGER.info(f'Output csv successfully created: {out_relative_path}')


def get_results(input_data: InputData, solar_potential_data: SolarPotentialData) -> Results:
    """Get graph, calculate your savings and mod quantity, and return your data objects."""
    LOGGER.info(f'Generating ResultsData for name: {input_data.name}')

    def _helper_calculate(func: Callable, zipped: tuple, arg3=None) -> FloatListMonthly:
        """Helper to clean up calculations for different monthly and annual figures."""
        out = []
        for arg1, arg2 in zipped:
            out.append(func(arg1, arg2, arg3))

        return out

    # Define out paths
    root_path = get_root(root_name='SolarCalculator')
    path_energy_graph = PurePath(fr"{root_path}/OutputGraphs/{input_data.name}-EnergyGraph.png")
    path_cost_graph = PurePath(fr"{root_path}/OutputGraphs/{input_data.name}-CostGraph.png")
    path_out_csv = PurePath(fr"{root_path}/OutputDataFiles/{input_data.name}-OutputData.csv")

    # Calculate Potential Cost, Savings, and Cost Reduction
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
        func=lambda a1, a2, a3: round(((a1 / a2) * 100), 2),
        zipped=zip(savings_monthly, input_data.cost_monthly)
    )
    # Create Data Frame with all data for graphing/writing outputs
    results_df = get_data_df(
        input_data=input_data,
        solar_potential_monthly=solar_potential_data.solar_potential_monthly,
        potential_cost_monthly=potential_cost_monthly,
        savings_monthly=savings_monthly,
        cost_reduction_monthly=cost_reduction_monthly,
    )
    create_comparison_graph(
        title=f"{input_data.name}'s Actual vs Potential Cost",
        d1=results_df['Cost $'].round(),
        d2=results_df['Potential Cost $'].round(),
        l1='Actual Cost',
        l2='Potential Cost',
        y_label='Dollars',
        out_path=path_cost_graph,
        graph_type='cost'
    )
    create_comparison_graph(
        title=f"{input_data.name}'s Energy Consumption vs Production",
        d1=results_df['Consumption kWh'],
        d2=results_df['Potential kWh'],
        l1='Energy Consumption',
        l2='Potential Energy Production',
        y_label=solar_potential_data.units_solar_potential,
        out_path=path_energy_graph,
        graph_type='energy'
    )
    create_out_csv(
        header={'Name': input_data.name,
                'Address': input_data.address,
                'Cost/kWh': input_data.cost_per_kwh,
                '': ''},  # Blank Row
        data_df=results_df,
        footer={'': '',   # Blank Row
                'Note:': solar_potential_data.note,
                'Potential kWh Source:': solar_potential_data.source},
        out_relative_path=path_out_csv
    )

    result = Results(
        name=input_data.name,
        address=input_data.address,
        actual_consumption_monthly=input_data.consumption_monthly,
        actual_cost_monthly=input_data.cost_monthly,
        potential_production_monthly=solar_potential_data.solar_potential_monthly,
        potential_cost_monthly=potential_cost_monthly,
        savings_monthly=savings_monthly,
        cost_reduction_monthly=cost_reduction_monthly,
        energy_graph_path=path_energy_graph,
        cost_graph_path=path_cost_graph,
        results_data_frame=results_df,
        results_csv_path=path_out_csv,
        mod_quantity=ceil(solar_potential_data.needed_kwh / input_data.mod_kwh),
        input_data=input_data,
        solar_potential_data=solar_potential_data
    )

    LOGGER.info(f'ResultsData successfully created and validated for name: {input_data.name}')
    return result


if __name__ == '__main__':
    pass
