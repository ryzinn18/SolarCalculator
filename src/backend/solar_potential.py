# solar_potential.py
# This module gets the solar iridescence for a given address.
"""
get_irid_object()'s call may need to be wrapped in a requests.exceptions.JSONDecodeError try/except statement.
Failed randomly with the above exception then worked the second time.
"""
from backend.utils import ListMonthly
from requests import get as r_get
from typing import Dict
from pydantic import BaseModel, PositiveInt


class SolarPotentialData(BaseModel):
    # Required
    address: str
    solar_potential_monthly: ListMonthly
    solar_potential_annual: PositiveInt
    needed_kwh: PositiveInt
    # Default
    note = "Iridescence reported over a 30 year average."
    units_solar_potential = "kiloWattHours"
    sym_solar_potential = "kWh"


def _get_params(capacity: int, address: str,
                azimuth="180", tilt="40", array_type="1", module_type="1", losses="10") -> Dict:
    """
    Get the parameters to be used to retrieve the iridescence info.
    :param capacity: String of the capacity of your solar array.
    :param address: String of the address you are analyzing. Must have street number, street name, and zip code.
    Everything except capacity and address are defaults provided by PV Watts. Modify them if you need to.
    :return: Dictionary of the params.
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


def _get_iridescence_obj(params: Dict) -> Dict:
    """Use requests lib to get iridescence object"""
    nrel_token = 'pzWxBOpm2FFksn0T13JLdJCJWjdsDSEYUOSjWQFu'
    request = r_get(
        url=f'https://developer.nrel.gov/api/pvwatts/v6.json?api_key={nrel_token}',
        params=params
    )
    return request.json()


def get_solar_potential(address: str, annual_consumption: int) -> SolarPotentialData:
    """
    ... WRITE THIS ...
    :param address: This is a string of the address. You need street number, street name, and zip code.
    :param annual_consumption: This is the actual annual consumption. Generated from input_handler.py
    :return ... THIS TOO ...
    """

    normal_params = _get_params(capacity=1, address=address)
    normal_outputs = _get_iridescence_obj(params=normal_params).get('outputs')
    normal_annual = round(normal_outputs.get('ac_annual'))

    needed_kwh = round(annual_consumption / normal_annual)

    actual_params = _get_params(capacity=needed_kwh, address=address)
    actual_obj = _get_iridescence_obj(params=actual_params)
    actual_outputs = actual_obj.get('outputs')
    actual_monthly = actual_outputs.get('ac_monthly')

    return SolarPotentialData(
        address=address,
        solar_potential_monthly=[round(elem) for elem in actual_monthly],
        solar_potential_annual=round(float(actual_outputs.get('ac_annual')), 2),
        needed_kwh=needed_kwh
    )


if __name__ == '__main__':
    pass
