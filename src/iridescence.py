# iridescence.py
# This module gets the solar iridescence for a given address.

from .utils import round_list_elems, get_out_obj
from requests import get as r_get
from typing import Dict, AnyStr


class Iridescence:
    NREL_TOKEN = 'pzWxBOpm2FFksn0T13JLdJCJWjdsDSEYUOSjWQFu'
    MOD_KWH = 0.4
    KEY_ACM = 'ac_monthly'
    KEY_ACA = 'ac_annual'

    def __init__(self, address: AnyStr, annual_consumption: AnyStr):
        """
        Upon initialization, each instance of this class will declare the monthly and annual AC solar potential based
        on the address and consumption parameters passed. Each instance will also have corresponding arrays for the
        months and year.
        :param address: This is a string of the address. You need street number, street name, and zip code.
        :param annual_consumption: This is the actual annual consumption. Generated from consumption.py
        """
        normal_params = self.get_params(capacity=1, address=address)
        normal_annual = round(self.get_irid_obj(params=normal_params)[self.KEY_ACA])

        needed_kwh = self.get_needed_kwh(consumption=annual_consumption, normal_annual=normal_annual)

        actual_params = self.get_params(capacity=needed_kwh, address=address)
        actual_obj = self.get_irid_obj(params=actual_params)
        actual_monthly = actual_obj[self.KEY_ACM]
        actual_annual = actual_obj[self.KEY_ACA]

        self.irid_monthly = round_list_elems(actual_monthly)
        self.irid_annual = round(actual_annual)
        self.irid_obj = get_out_obj(self.irid_monthly, self.irid_annual)
        self.note = "Iridescence reported over a 30 year average."

    def __repr__(self):
        return (
                f"Iridescence:\n"
                + f"\tNOTE: Iridescence reported over a 30 year average.\n"
                + f"\tannual iridescence = {self.irid_annual}\n"
                + f"\tmonthly iridescence = {self.irid_monthly}\n"
        )

    @staticmethod
    def get_params(capacity: int, address: AnyStr,
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

    @staticmethod
    def get_irid_obj(params: Dict) -> Dict:
        """Use requests lib to get iridescence object"""
        request = r_get(
            url=f'https://developer.nrel.gov/api/pvwatts/v6.json?api_key={Iridescence.NREL_TOKEN}',
            params=params
        )
        return request.json()['outputs']

    @staticmethod
    def get_needed_kwh(consumption: int, normal_annual: int) -> int:
        """Quick Maths for needed kwh based on actual consumption and normalized consumption"""
        return round(consumption / normal_annual)


if __name__ == "__main__":
    print(Iridescence("1417 Bath Street, 93101", "6575"))