# iridescence.py
# This module gets the solar iridescence for a given address.
from requests import get as r_get
from typing import Dict, AnyStr, List
from pydantic import BaseModel, conint, conlist, PositiveInt
from utils import ListMonthly

NREL_TOKEN = 'pzWxBOpm2FFksn0T13JLdJCJWjdsDSEYUOSjWQFu'


class SolarPotentialData(BaseModel):
    # Mandatory
    address: str
    solar_potential_monthly: ListMonthly
    solar_potential_annual: PositiveInt
    # Default
    note = "Iridescence reported over a 30 year average."
    units_solar_potential = "kiloWattHours"
    sym_solar_potential = "kWh"


def _get_params(capacity: PositiveInt, address: AnyStr,
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


def _get_irid_obj(params: Dict) -> Dict:
    """Use requests lib to get iridescence object"""
    request = r_get(
        url=f'https://developer.nrel.gov/api/pvwatts/v6.json?api_key={NREL_TOKEN}',
        params=params
    )
    return request.json()['outputs']


def _get_needed_kwh(consumption: PositiveInt, normal_annual: PositiveInt) -> PositiveInt:
    """Quick Maths for needed kwh based on actual consumption and normalized consumption."""
    return round(consumption / normal_annual)


def get_solar_potential(address: AnyStr, annual_consumption: AnyStr) -> SolarPotentialData:
    """
    Upon initialization, each instance of this class will declare the monthly and annual AC solar potential based
    on the address and consumption parameters passed. Each instance will also have corresponding arrays for the
    months and year.
    :param address: This is a string of the address. You need street number, street name, and zip code.
    :param annual_consumption: This is the actual annual consumption. Generated from input_handler.py
    """

    normal_params = _get_params(capacity=1, address=address)
    normal_annual = round(_get_irid_obj(params=normal_params).get('ac_annual'))

    needed_kwh = _get_needed_kwh(consumption=int(annual_consumption), normal_annual=normal_annual)

    actual_params = _get_params(capacity=needed_kwh, address=address)
    actual_obj = _get_irid_obj(params=actual_params)
    actual_monthly = actual_obj['ac_monthly']

    return SolarPotentialData(
        address=address,
        solar_potential_monthly=[round(elem) for elem in actual_monthly],
        solar_potential_annual=round(sum(actual_monthly))
    )


if __name__ == "__main__":
    print(get_solar_potential("1417 Bath Street, 93101", "6575"))