# samples.sample_data_object.py
from backend.input_handler import InputData
from backend.solar_potential import SolarPotentialData
from backend.results import Results
from pathlib import PurePath
from os import getcwd
from os.path import join

SAMPLE_INPUT_DATA = InputData(
    name="RyanTest",
    address="1417 Bath Street, 93101",
    mod_kwh=0.4,
    consumption_monthly=[820, 780, 760, 740, 740, 710, 705, 705, 710, 702, 750, 780],
    consumption_annual=8912,
    cost_monthly=[155.8, 148.2, 144.4, 140.6, 140.6, 134.9, 133.95, 135.85, 134.85, 133.38, 142.5, 147.2],
    cost_annual=1693.28,
    cost_per_kwh=0.19
)

SAMPLE_SOLAR_POTENTIAL_DATA = SolarPotentialData(
    address=SAMPLE_INPUT_DATA.address,
    solar_potential_monthly=[436, 439, 556, 618, 661, 603, 650, 647, 567, 526, 457, 405],
    solar_potential_annual=6565,
    needed_kwh=4
)

SAMPLE_RESULTS = Results(
    name=SAMPLE_INPUT_DATA.name,
    address=SAMPLE_INPUT_DATA.address,
    potential_cost_monthly=[72.96, 64.79, 38.76, 23.18, 15.01, 20.33, 10.45, 12.92, 27.17, 33.44, 55.67, 71.25],
    potential_cost_annual=445.93,
    savings_monthly=[82.84, 83.41, 105.64, 117.42, 125.59, 114.57, 123.5, 122.93, 107.73, 99.94, 86.83, 76.95],
    savings_annual=1247.35,
    cost_reduction_monthly=[47, 44, 27, 16, 11, 15, 8, 10, 20, 25, 39, 48],
    cost_reduction_annual=26,
    graph_path=join(getcwd(), PurePath(fr"./OutputGraphs/{SAMPLE_INPUT_DATA.name}-SolarGraph.png")),
    mod_quantity=15,
    input_data=SAMPLE_INPUT_DATA,
    solar_potential_data=SAMPLE_SOLAR_POTENTIAL_DATA
)

SAMPLE_SHEET = '1gneTmzTrGTsJIrjkjzEOYS-Bq7irB_WZ2TJWXMlFp4k'
SAMPLE_CSV = r'./samples/sample_consumption.csv'
SAMPLE_XLSX = r'./samples/sample_consumption.xlsx'
SAMPLE_OUT_RELATIVE_PATH = PurePath(fr"./OutputGraphs/{SAMPLE_INPUT_DATA.name}-SolarGraph.png")

if __name__ == '__main__':
    pass
