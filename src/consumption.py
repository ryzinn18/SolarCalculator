"""
I have a lot of thoughts about this one. I would like for multiple ways in input the annual consumption:
- upload a .csv or .xlsx
- upload via a google sheet?
- upload via python:
    - probably just using input() initially
    - maybe eventually will have a basic website UI and can input there?

Should probably start with just a simple python class.
- could eventually have a parent class and each of the above options could be child classes?
- could have a handler which decides how to convert the input data from the options above into a uniform class.
"""
from utils import MONTHS_MAP


class Consumption:

    def __init__(self):

        self.cons_monthly = self.get_monthly()
        self.cons_annual = self.get_annual(monthly=self.cons_monthly)
        self.cons_obj: dict

    def __repr__(self):
        return (
                f"Consumption:\n"
                + f"\tannual consumption = f{self.cons_annual}\n"
                + f"\tmonthly consumption = f{self.cons_monthly}\n"
        )

    @staticmethod
    def get_monthly() -> list[int]:
        # return [1481, 1317, 1664, 2294, 1938, 1829, 3212, 2641, 2194, 1771, 1678, 1713]

        print("Please enter the monthly kWh consumption for:")
        monthly = []
        for i in range(1, 13):
            monthly.append(int(input(f"\t{MONTHS_MAP[i]}")))
        return monthly

    @staticmethod
    def get_annual(monthly: list) -> int:
        return sum(monthly)


if __name__ == "__main__":
    Consumption()