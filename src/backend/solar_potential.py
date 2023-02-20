# SolarCalculator/src/backend/solar_potential.py
# This module gets the solar iridescence data for a given address.
from requests import get as r_get
from utils import SolarPotentialData, EventReadyForResults, Status
from config import NREL_API_KEY
from logging import getLogger
from json import JSONDecodeError


LOGGER = getLogger(__name__)


def _get_params(capacity: int, address: str,
                azimuth="180", tilt="40", array_type="1", module_type="1", losses="10") -> dict:
    """
    Get the parameters to be used to retrieve the iridescence info.
    :param capacity: String of the capacity of your solar array.
    :param address: String of the address you are analyzing. Must have street number, street name, and zip code.
    Everything except capacity and address are defaults provided by PV Watts. Modify them if you need to.
    :return: dictionary of the params.
    """

    return {
        "system_capacity": str(capacity),
        "azimuth": azimuth,
        "tilt": tilt,
        "array_type": array_type,
        "module_type": module_type,
        "losses": losses,
        "address": address
    }


def _get_iridescence_obj(params: dict, nrel_token: str) -> dict:
    """Use requests lib to get iridescence object via the nrel token passed."""

    LOGGER.info(f'Requesting the nrel api to retrieve solar potential data using token: {nrel_token}')

    request, i = None, 0
    while i < 3:
        try:
            # Try the get request with the nrel api.
            request = r_get(
                url=f'https://developer.nrel.gov/api/pvwatts/v6.json?api_key={nrel_token}',
                params=params
            )
        except JSONDecodeError:
            # This is a rare error that is typically alleviated by recalling the get request.
            # If encountered, recall the get function a max of 3 times.
            LOGGER.error('JSONDecodeError encountered. Attempting the call again', exc_info=True)
            i += 1
            continue
        except Exception as e:
            # Log and raise the appropriate exception if encountered.
            LOGGER.error(e, exc_info=True)
            raise e
        else:
            # Return the requested data if request successful.
            LOGGER.info(f'Request successful for solar potential data: {request.json()}')
            return request.json()

    # If the loop exits then it is because the JSONDecodeError was raised 3 times in a row.
    # Log the issue and raise an Exception.
    LOGGER.error('The nrel API get request still failed due to a JSONDecodeError after 3 requests')
    raise Exception('After requesting 3 times, the nrel API get request still failed due to a JSONDecodeError.')


def get_solar_potential(input_data: dict) -> SolarPotentialData:
    """
    Runs through steps to get solar potential data for the address provided:
    1. Get normalized data:
        - Get params with capacity == 1 (normalized)
        - Get iridescence data for normal params
    2. Calculate needed kWh:
        - Divide actual annual consumption by normalized annual consumption
    3. Get solar potential data:
        - Get params with capacity == needed kWh (actual)
    4. Validate actual data into SolarPotentialData model.

    :param input_data: Dict (json) object passed to this function containing address and consumption_annual attributes.
    :return SolarPotentialData model
    """

    LOGGER.info(f'solar_potential_handler() called for given event: {input_data}')

    # if not input_data.get('uid') or not input_data.get('address') or not input_data.get('consumption_annual'):
    #     LOGGER.error(f'The event passed to solar_potential_handler() does not have necessary attribute(s).')
    #     raise KeyError('The event passed to solar_potential_handler() does not have necessary attribute(s).')

    address = input_data.get('address')
    annual_consumption = input_data.get('consumption_annual')

    LOGGER.info(f'Attempting to retrieve the solar potential data for the following address: {address}')

    # 1. Get normalized data:
    normal_params = _get_params(capacity=1, address=address)
    normal_outputs = _get_iridescence_obj(params=normal_params, nrel_token=NREL_API_KEY).get('outputs')
    normal_annual = round(normal_outputs.get('ac_annual'))
    # 2. Calculate needed kWh:
    needed_kwh = round(annual_consumption / normal_annual)
    # 3. Get solar potential data:
    actual_params = _get_params(capacity=needed_kwh, address=address)
    actual_obj = _get_iridescence_obj(params=actual_params, nrel_token=NREL_API_KEY)
    actual_outputs = actual_obj.get('outputs')
    actual_monthly = actual_outputs.get('ac_monthly')
    # 4. Validate actual data into SolarPotentialData model.
    result = SolarPotentialData(
        uid=input_data.get('uid'),
        address=address,
        solar_potential_monthly=[round(elem) for elem in actual_monthly],
        solar_potential_annual=round(float(actual_outputs.get('ac_annual')), 2),
        needed_kwh=needed_kwh,
        input_data=input_data
    )

    LOGGER.info(f'Solar data retrieved and validated: {result}')
    return result


def solar_potential_handler(event: dict, context) -> dict:
    """AWS Lambda Handler for calling get_solar_potential() and returning proper event object."""

    LOGGER.info(f'Called Lambda Handler function for getting solar data event for uid: {event["uid"]}')

    input_data = event['input_data']
    # Handle getting the necessary data
    try:
        solar_data = get_solar_potential(input_data=input_data)
        status = Status(status_code=200, message="get_solar_potential() called successfully.")
        LOGGER.info(f'Lambda Handler for solar data successfully executed for uid: {event["uid"]}')
    except Exception as e:
        solar_data = dict()
        status = Status(status_code=400, message=f"get_solar_potential() called unsuccessfully due to error: {e.__repr__()}")
        LOGGER.error(e, exc_info=True)

    return EventReadyForResults(
        uid=event['uid'],
        time_stamp=event['time_stamp'],
        status=status,
        input_data=input_data,
        solar_data=solar_data
    ).dict()


if __name__ == '__main__':
    from utils import SAMPLES, import_json
    print(solar_potential_handler(event=import_json(SAMPLES['event_ready_for_solar']), context=None)['status'])
    pass
