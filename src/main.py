# SolarCalculator/src/main.py
# This is the main module for running this program.
from utils import SAMPLES, import_json
from backend.inputs import get_inputs
from backend.solar_potential import get_solar_potential
from backend.results import get_results
from logging import getLogger

LOGGER = getLogger(__name__)


def main(event: dict, context) -> dict:
    """SolarCalculator's main function. Set up to run locally or via AWS Lambda."""

    LOGGER.info('main() called.')

    # Get Input data
    data_input = get_inputs(
        input_event=event,
    )

    LOGGER.info(f'InputData successfully received for uid: {data_input.uid}')

    # Get Solar Potential data
    data_solar_potential = get_solar_potential(
        input_data=data_input
    )
    LOGGER.info(f'SolarPotentialData data successfully received for uid: {data_solar_potential.uid}')

    # Get Results data
    data_results = get_results(
        input_data=data_input,
        solar_data=data_solar_potential
    )
    LOGGER.info(f'Results data successfully received for: {data_results.uid}')

    return data_results.dict()


if __name__ == '__main__':
    main(event=import_json(SAMPLES['event_valid_form']), context=None)
    pass
