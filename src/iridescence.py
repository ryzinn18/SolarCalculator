# iridescence.py
# This module gets the solar iridescence for a given address.

import requests


class Iridescence:
    NREL_KEY = 'pzWxBOpm2FFksn0T13JLdJCJWjdsDSEYUOSjWQFu'
    MOD_KWH = 0.4

    def __init__(self, address: str, consumption: str):
        """
        Upon initialization, each instance of this class will declare the monthly and annual AC solar potential based
        on the address and consumption parameters passed. Each instance will also have corresponding arrays for the
        months and year.
        :param address: This is a string of the address. You need street number, street name, and zip code.
        :param consumption: This is the actual annual consumption. Generated from consumption.py
        """
        normal_params = self.get_params(capacity="1", address=address)
        normal_annual = self.get_irid_obj(params=normal_params)['ac_annual']

        needed_kwh = self.get_needed_kwh(consumption=consumption, normal_annual=normal_annual)

        actual_params = self.get_params(capacity=needed_kwh, address=address)
        actual_obj = self.get_irid_obj(params=actual_params)
        actual_monthly = actual_obj['ac_monthly']
        actual_annual = actual_obj['ac_annual']

        self.irid_monthly = self.get_clean_monthly(actual_monthly)
        self.irid_annual = self.get_clean_annual(actual_annual)
        self.irid_obj = self.get_out_obj(self.irid_monthly, self.irid_annual)

    def __repr__(self):
        return (
                f"Iridescence:\n"
                + f"\tNOTE: Iridescence reported is over a 30 year average.\n"
                + f"\tannual iridescence = f{self.irid_annual}\n"
                + f"\tmonthly iridescence = f{self.irid_monthly}\n"
        )

    @staticmethod
    def get_params(capacity: str, address: str,
                   azimuth="180", tilt="40", array_type="1", module_type="1", losses="10") -> dict:
        """
        Get the parameters to be used to retreive the iridescence info.
        :param capacity: String of the capacity of your solar array.
        :param address: String of the address you are analyzing. Must have street number, street name, and zip code.
        Everything except capacity and address are defaults provided by PV Watts. Modify them if you need to.
        :return: Dictionary of the params.
        """
        return {
            "system_capacity": capacity,
            "azimuth": azimuth,
            "tilt": tilt,
            "array_type": array_type,
            "module_type": module_type,
            "losses": losses,
            "address": address
        }

    @staticmethod
    def get_irid_obj(params: dict) -> dict:
        """Use requests lib to get iridescence object"""
        r = requests.get(
            url=f'https://developer.nrel.gov/api/pvwatts/v6.json?api_key={Iridescence.NREL_KEY}',
            params=params
        )
        return r.json()['outputs']

    @staticmethod
    def get_needed_kwh(consumption: str, normal_annual: str) -> str:
        """Quick Maths for needed kwh based on actual consumption and normalized consumption"""
        return str(round((float(consumption) / float(normal_annual)), 2))

    @staticmethod
    def get_clean_monthly(monthly: list) -> list:
        """Clean up the monthly list by converting to strings and rounding to 2 decimal spaces"""
        return [str(round(month, 2)) for month in monthly]

    @staticmethod
    def get_clean_annual(annual: float) -> str:
        """Quick function to convert the float ac_annual figure to a string with 2 decimal places"""
        return str(round(annual, 2))

    @staticmethod
    def get_out_obj(monthly, annual) -> dict:
        """Generate an output object for the instance of the class"""
        out_obj = {'annual': annual}
        for i, month in enumerate(monthly, 1):
            out_obj[i] = month

        return out_obj


if __name__ == "__main__":
    print(Iridescence("1417 Bath Street, 93101", "6575.31"))