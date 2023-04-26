# SolarCalculator/src/backend/solar_potential.py
# This module gets the solar iridescence data for a given address.
from requests import get as r_get

from logging import getLogger
from json import JSONDecodeError
from datetime import datetime as dt

from config import NREL_API_KEY

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


def get_solar_potential(input_data: dict) -> dict:
    """Call NREL's API for solar data related to array location (address) and capacity."""

    LOGGER.info(f'get_solar_potential() called for uid: {input_data.get("uid")}')

    # Get data:
    params = _get_params(capacity=input_data.get('capacity'), address=input_data.get('address'))
    response = _get_iridescence_obj(params=params, nrel_token=NREL_API_KEY)
    # Organize data:
    if response.get('errors'):
        LOGGER.info(f'_get_iridescence_obj() response returned errors for uid: {input_data.get("uid")}')
        return {
            'uid': input_data.get("uid"),
            'errors': response.get('errors'),
            'status': {
                'status_code': 422,
                'message': "_get_iridescence_obj() response returned errors."
            }
        }
    else:
        LOGGER.info(f'get_solar_potential() called successfully for uid: {input_data.get("uid")}')
        return {
            'uid': input_data.get("uid"),
            'output_monthly': [round(elem) for elem in response.get('outputs').get('ac_monthly')],
            'output_annual': round(float(response.get('outputs').get('ac_annual')), 2),
            'state': response.get('station_info').get('state'),
            'status': {
                'status_code': 200,
                'message': "_get_iridescence_obj() called successfully."
            }
        }


def solar_potential_handler(event: dict, context) -> dict:
    """Handler for calling get_solar_potential() and returning validated object."""

    LOGGER.info(f'Called Handler function for getting solar data event for uid: {event.get("uid")}')

    # Handle getting the necessary data
    try:
        solar_data = get_solar_potential(input_data=event)
    except Exception as e:
        uid = event.get("uid") if event.get("uid") else f"NA-{dt.now().__str__().replace(' ', '_').replace(':', '.')}"
        solar_data = {
            "uid": uid,
            "status": {
                "status_code": 400,
                "message": f"get_solar_potential() called unsuccessfully due to error: {e.__repr__()}"
            }
        }
        LOGGER.error(f'Lambda Handler for solar data failed for uid: {uid}')
        LOGGER.error(e, exc_info=True)

    return solar_data


if __name__ == '__main__':
    from utils import SAMPLES, import_json
    print(solar_potential_handler(event=import_json(SAMPLES['event_ready_for_solar'])).get("status"))
