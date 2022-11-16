"""
ToDo (smaller):

ToDo (large):
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
from samples.sample_data_objects import SAMPLE_CSV, SAMPLE_XLSX, SAMPLE_SHEET, \
    SAMPLE_INPUT_DATA, SAMPLE_SOLAR_POTENTIAL_DATA


def main() -> Results:
    """ data_input = input_handler(
        input_type='sheet',
        input_source=SAMPLE_SHEET
    )
    data_solar_potential = get_solar_potential(
        address=data_input.address,
        annual_consumption=data_input.consumption_annual
    )"""

    return get_results(input_data=SAMPLE_INPUT_DATA, solar_potential_data=SAMPLE_SOLAR_POTENTIAL_DATA)


if __name__ == '__main__':
    main()
