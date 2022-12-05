"""
ToDo (smaller):
- Restructure repo:
    - update __init__.py in backend directory so that can inport any backend object from single line
- Get real values for samples.

ToDo (large):
- Add logging functionality.
- Top down documentation.
- Unit tests all modules.
- Create web UI (JavaScript).
    - Build UI.
    - Build APIs.
- Package!
"""
from backend.input_handler import input_handler
from backend.solar_potential import get_solar_potential
from backend.results import get_results, Results
from pathlib import PurePath

SAMPLES = {
    'sheet': '1gneTmzTrGTsJIrjkjzEOYS-Bq7irB_WZ2TJWXMlFp4k',
    'csv': r'./samples/sample_consumption.csv',
    'xlsx': r'./samples/sample_consumption.xlsx',
    'out': PurePath(fr"./OutputGraphs/RyanZinniger-SolarGraph.png"),
}


def main() -> Results:
    data_input = input_handler(
        input_type='sheet',
        input_source=SAMPLES['sheet']
    )
    data_solar_potential = get_solar_potential(
        address=data_input.address,
        annual_consumption=data_input.consumption_annual
    )
    data_results = get_results(input_data=data_input, solar_potential_data=data_solar_potential)

    return data_results


if __name__ == '__main__':
    main()

