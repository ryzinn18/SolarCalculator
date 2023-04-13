# # SolarCalculator/src/main.py
# This is the main module for running this program.
from logging import getLogger, basicConfig, ERROR

from utils import check_http_response, Status

from inputs import input_handler
from solar_potential import solar_potential_handler
from results import results_handler

basicConfig(
    # filename='src/logs/main.log', # When running flask app
    filename='logs/main.log',
    level=ERROR,
    format='%(levelname)s:%(filename)s:%(asctime)s:%(funcName)s(): %(message)s',
    datefmt='%Y/%m/%d-%H.%M.%S',
    filemode='w',
)

LOGGER = getLogger(__name__)


def main_handler(event: dict, context) -> dict:
    """SolarCalculator's main function. Set up to run locally or via AWS Lambda."""

    LOGGER.info('main_handler() called.')

    # Get Input data
    data_input = input_handler(
        event=event,
    )
    if not check_http_response(response_code=data_input.get("status").get("status_code")):
        LOGGER.error(
            f'InputData was returned with a {data_input.get("status").get("status_code")} status code  '
            f'and the following message: {data_input.get("status").get("message")}')
    LOGGER.info(f'InputData successfully received for uid: {data_input.get("uid")}')

    # Get Solar Potential data
    data_solar_potential = solar_potential_handler(
        event=data_input,
    )
    if not check_http_response(response_code=data_solar_potential.get("status").get("status_code")):
        LOGGER.error(
            f'InputData was returned with a {data_solar_potential.get("status").get("status_code")} status code  '
            f'and the following message: {data_solar_potential.get("status").get("message")}')
    LOGGER.info(f'SolarPotentialData data successfully received for uid: {data_solar_potential.get("uid")}')

    # Get Results data
    data_results = results_handler(
        input_data=data_input,
        solar_data=data_solar_potential
    )
    if not check_object(data_results):
        LOGGER.error(
            f'InputData was returned with a X status code  '
            + f'and the following message: Y')
    LOGGER.info(f'Results data successfully received for: {data_results.get("uid")}')

    return data_results


if __name__ == '__main__':
    from utils import import_json, SAMPLES

    OUT = main_handler(event=import_json(SAMPLES['event_valid_form']), context=None)
    print(OUT)
    # print("STATUS_CODE: ", OUT.get('status').get('status_code'))
    # print("MOD_QUANTITY: ", OUT.get('mod_quantity'))
