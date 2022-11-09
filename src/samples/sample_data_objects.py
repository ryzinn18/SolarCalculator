# samples.sample_data_object.py
from backend.input_handler import InputData
from backend.solar_potential import SolarPotentialData
from backend.results import Results
from backend.utils import get_absolute_path
from pathlib import PurePath

SAMPLE_INPUT_DATA = InputData(
    name="RyanTest",
    address="1417 Bath Street, 93101",
    mod_kwh=0.4,
    consumption_monthly=[436, 439, 556, 618, 661, 603, 650, 647, 567, 526, 457, 405],
    consumption_annual=23661,
    cost_monthly=[130, 101, 146, 199, 179, 170, 220, 178, 131, 126, 121, 135],
    cost_annual=1836,
    cost_per_kwh=0.08
)

SAMPLE_SOLAR_POTENTIAL_DATA = SolarPotentialData(
    address=SAMPLE_INPUT_DATA.address,
    solar_potential_monthly=[436, 439, 556, 618, 661, 603, 650, 647, 567, 526, 457, 405],
    solar_potential_annual=6565,
    needed_kwh=4
)

SAMPLE_RESULTS = Results(
    name=SAMPLE_INPUT_DATA.name,
    graph_path=get_absolute_path(relative_path=PurePath(fr"./OutputGraphs/{SAMPLE_INPUT_DATA.name}-SolarGraph.png")),
    savings=1000,
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
