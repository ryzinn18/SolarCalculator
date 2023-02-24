# SolarCalculator/src/main.py
# This is the main module for running this program.
from utils import SAMPLES, import_json
from backend.inputs import input_handler
from backend.solar_potential import solar_potential_handler
from backend.results import results_handler
from logging import getLogger

LOGGER = getLogger(__name__)


def main_handler(event: dict, context) -> dict:
    """SolarCalculator's main function. Set up to run locally or via AWS Lambda."""

    LOGGER.info('main() called.')

    # Get Input data
    data_input = input_handler(
        event=event,
        context=context
    )

    LOGGER.info(f'InputData successfully received for uid: {data_input["uid"]}')

    # Get Solar Potential data
    data_solar_potential = solar_potential_handler(
        event=data_input,
        context=context
    )
    LOGGER.info(f'SolarPotentialData data successfully received for uid: {data_solar_potential["uid"]}')

    # Get Results data
    data_results = results_handler(
        event=data_solar_potential,
        context=context
    )
    LOGGER.info(f'Results data successfully received for: {data_results["uid"]}')

    return data_results


if __name__ == '__main__':
    OUT = main_handler(event=import_json(SAMPLES['event_valid_form']), context=None)
    print("STATUS_CODE: ", OUT['status']['status_code'])
    print("MOD_QUANTITY: ", OUT['results_data']['mod_quantity'])
