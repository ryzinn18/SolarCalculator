# solar_potential.py
# This module gets the solar iridescence for a given address.
"""
Notes:
- get_irid_object()'s call may need to be wrapped in a requests.exceptions.JSONDecodeError try/except statement.
Failed randomly with the above exception then worked the second time.
- personal nrel token: pzWxBOpm2FFksn0T13JLdJCJWjdsDSEYUOSjWQFu
"""
from backend.utils import IntListMonthly, LOGGER
from requests import get as r_get
from pydantic import BaseModel, PositiveInt


class SolarPotentialData(BaseModel):
    # Required
    address: str
    solar_potential_monthly: IntListMonthly
    solar_potential_annual: PositiveInt
    needed_kwh: PositiveInt
    # Default
    note = "Solar potential (kWh) reported over a 30 year average."
    source = "pvwatts.nrel.gov/pvwatts.php"
    units_solar_potential = "kiloWattHours"
    sym_solar_potential = "kWh"


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


def _get_iridescence_obj(params: dict) -> dict:
    """Use requests lib to get iridescence object"""

    nrel_token = 'pzWxBOpm2FFksn0T13JLdJCJWjdsDSEYUOSjWQFu'
    LOGGER.info(f'Requesting the nrel api to retrieve solar potential data using token: {nrel_token}')

    try:
        # Try the request
        request = r_get(
            url=f'https://developer.nrel.gov/api/pvwatts/v6.json?api_key={nrel_token}',
            params=params
        )
    except Exception as e:
        # Log and raise the appropriate exception if encountered
        LOGGER.error(e, exc_info=True)
        raise e
    else:
        # Return the requested data if request successful
        LOGGER.info(f'Request successful for solar potential data: {request.json()}')
        return request.json()


def get_solar_potential(address: str, annual_consumption: int) -> SolarPotentialData:
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

    :param address: String of the address. Best as "<street number> <street name>, <zip code>"
    :param annual_consumption: This is the actual annual consumption. Generated from inputs.py
    :return SolarPotentialData model
    """

    LOGGER.info(f'Attempting to retrieve the solar potential data for the following address: {address}')

    # 1. Get normalized data:
    normal_params = _get_params(capacity=1, address=address)
    normal_outputs = _get_iridescence_obj(params=normal_params).get('outputs')
    normal_annual = round(normal_outputs.get('ac_annual'))
    # 2. Calculate needed kWh:
    needed_kwh = round(annual_consumption / normal_annual)
    # 3. Get solar potential data:
    actual_params = _get_params(capacity=needed_kwh, address=address)
    actual_obj = _get_iridescence_obj(params=actual_params)
    actual_outputs = actual_obj.get('outputs')
    actual_monthly = actual_outputs.get('ac_monthly')
    # 4. Validate actual data into SolarPotentialData model.
    result = SolarPotentialData(
        address=address,
        solar_potential_monthly=[round(elem) for elem in actual_monthly],
        solar_potential_annual=round(float(actual_outputs.get('ac_annual')), 2),
        needed_kwh=needed_kwh
    )

    LOGGER.info(f'Solar data retrieved and validated: {result}')
    return result


if __name__ == '__main__':
    pass
