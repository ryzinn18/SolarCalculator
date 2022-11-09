from backend.utils import MONTHS_MAP, get_absolute_path
from backend.solar_potential import SolarPotentialData
from backend.input_handler import InputData
from os import PathLike
from pathlib import PurePath
from math import ceil
import matplotlib.pyplot as plt
from pydantic import BaseModel, PositiveInt, FilePath


class Results(BaseModel):
    # Required
    name: str
    graph_path: FilePath
    savings: float
    mod_quantity: PositiveInt
    input_data: InputData
    solar_potential_data: SolarPotentialData


def _get_graph(input_data: InputData, solar_potential_data: SolarPotentialData,
               out_relative_path: PathLike[str]) -> PathLike[str]:
    """Generate the Results graph."""
    potential = solar_potential_data.solar_potential_monthly    # np.array
    consumption = input_data.consumption_monthly                # np.array
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

    return get_absolute_path(relative_path=out_relative_path)


def get_results(input_data: InputData, solar_potential_data: SolarPotentialData) -> Results:
    """Get graph, calculate your savings and mod quantity, and return your data objects."""
    relative_graph_path = PurePath(fr"./OutputGraphs/{input_data.name}-SolarGraph.png")

    graph_path = _get_graph(
        input_data=input_data,
        solar_potential_data=solar_potential_data,
        out_relative_path=relative_graph_path
    )
    savings = (input_data.cost_annual - (solar_potential_data.solar_potential_annual * input_data.cost_per_kwh))

    return Results(
        name=input_data.name,
        graph_path=graph_path,
        savings=round(savings, 2),
        mod_quantity=ceil(solar_potential_data.needed_kwh / input_data.mod_kwh),
        input_data=input_data,
        solar_potential_data=solar_potential_data
    )

