# SolarCalculator/src/main.py
# This is the main module for running this program locally.
# This module also configures the logger.
from utils import SAMPLES, import_json
from backend import inputs as inp, solar_potential as sp, results as res
from logging import getLogger

LOGGER = getLogger(__name__)


def main():
    LOGGER.info('main() called.')

    # Get Input data
    data_input = inp.input_handler(
        event=import_json(SAMPLES['event_valid_form']),
        context=None
    )

    LOGGER.info(f'InputData successfully received for uid: {data_input["uid"]}')

    # Get Solar Potential data
    data_solar_potential = sp.solar_potential_handler(
        event=data_input,
        context=None
    )
    LOGGER.info(f'SolarPotentialData data successfully received for uid: {data_solar_potential["uid"]}')

    # Get Results data
    data_results = res.results_handler(
        event=data_solar_potential,
        context=None
    )
    LOGGER.info(f'Results data successfully received for: {data_results["uid"]}')

    return data_input


if __name__ == '__main__':
    main()
