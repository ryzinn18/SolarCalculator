"""
ToDo (smaller):

ToDo (large):
- Unit tests all modules.
- Create web UI (JavaScript).
    - Build UI.
    - Build APIs.
- Top down documentation.
- Package!
"""
from backend.input_handler import input_handler
from backend.solar_potential import get_solar_potential
from backend.results import get_results, Results
from samples.sample_data_objects import SAMPLE_CSV, SAMPLE_XLSX, SAMPLE_SHEET


def main() -> Results:

    data_input = input_handler(
        input_type='csv',
        input_source=SAMPLE_CSV
    )
    data_solar_potential = get_solar_potential(
        address=data_input.address,
        annual_consumption=data_input.consumption_annual
    )

    return get_results(input_data=data_input, solar_potential_data=data_solar_potential)


if __name__ == '__main__':
    # main()
    from os import getcwd, listdir
    print(listdir(getcwd()))
