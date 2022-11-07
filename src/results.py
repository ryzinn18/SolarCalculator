from .utils import MONTHS_MAP
from .solar_potential import SolarPotentialData
from .input_handler import InputData
from os import getcwd
from math import ceil
import numpy as np
import matplotlib.pyplot as plt
from pydantic import BaseModel, PositiveInt


class Results(BaseModel):
    # Required
    name: str
    graph_path: str
    savings: float
    mod_quantity: PositiveInt
    input_data: InputData
    solar_potential_data: SolarPotentialData


def _get_graph(input_data: InputData, solar_potential_data: SolarPotentialData) -> str:
    """Generate the Results graph."""
    out_relative_path = fr"./OutputGraphs/{input_data.name}-SolarGraph.png"
    potential = np.array(solar_potential_data.solar_potential_monthly)
    consumption = np.array(input_data.consumption_monthly)
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

    return getcwd() + out_relative_path[1:]


def get_results(input_data: InputData, solar_potential_data: SolarPotentialData) -> Results:
    """Get graph, calculate your savings and mod quantity, and return your data objects."""

    return Results(
        name=input_data.name,
        graph_path=_get_graph(
            input_data=input_data,
            solar_potential_data=solar_potential_data
        ),
        savings=round(
            number=(input_data.cost_annual - (solar_potential_data.solar_potential_annual * input_data.cost_per_kwh)),
            ndigits=2
        ),
        mod_quantity=ceil(solar_potential_data.needed_kwh / input_data.mod_kwh),
        input_data=input_data,
        solar_potential_data=solar_potential_data
    )




