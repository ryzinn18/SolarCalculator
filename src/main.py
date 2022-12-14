"""
ToDo (smaller):
- Restructure repo:
    - update __init__.py in backend directory so that can inport any backend object from single line
- Get real values for samples.

ToDo (large):
- Top down documentation.
- Unit tests all modules.
- Create web UI (JavaScript).
    - Build UI.
    - Build APIs.
- Package!
"""
from utils import SAMPLES, export_json, import_json
from backend import inputs as inp, solar_potential as sp, results as res, LOGGER, \
    get_data_df

_INPUT_VALID = import_json(SAMPLES['input_valid'])
_INPUT_INVALID = import_json(SAMPLES['input_invalid_value'])

_SOLAR_POTENTIAL_VALID = import_json(SAMPLES['solar_potential_valid'])

_RESULT_VALID = import_json(SAMPLES['results_valid'])


def main():
    LOGGER.info('main() called.')

    # Get Input data
    data_input = inp.input_handler(
        input_type='csv',
        input_source=SAMPLES['csv_valid']
    )
    LOGGER.info(f'InputData successfully received for name {data_input.name}')
    #
    # # Get Solar Potential data
    # data_solar_potential = sp.get_solar_potential(
    #     address=data_input.address,
    #     annual_consumption=data_input.consumption_annual
    # )
    # LOGGER.info(f'SolarPotentialData data successfully received for address {data_solar_potential.address}')
    #
    # # Get Results data
    # data_results = res.get_results(input_data=data_input, solar_potential_data=data_solar_potential)
    # LOGGER.info(f'ResultsData successfully received for {data_results.name}')

    return data_input


if __name__ == '__main__':
    main()

