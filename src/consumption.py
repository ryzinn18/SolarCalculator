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

# from utils import MONTHS_MAP
from typing import List, AnyStr, Dict

MONTHS_MAP = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}


def csv_consumption(file_path: AnyStr) -> List[int]:
    """Call this function to read a csv with specified format for monthly consumption."""
    from csv import reader

    monthly = []
    with open(file_path, 'r') as file:
        csv = reader(file)
        next(csv)
        for row in csv:
            monthly.append(int(round(float(row[2]), 0)))

    return monthly


def xlsx_consumption(file_path: AnyStr) -> List[int]:
    """Call this function to read a xlsx with specified format for monthly consumption."""
    from openpyxl import load_workbook
    sheet = load_workbook(file_path)['Sheet1']

    monthly = []
    for i in range(2, 14):
        monthly.append(int(sheet[f'C{i}'].value))

    return monthly


def manual_input_consumption() -> List[int]:
    """Get monthly consumption via python input()"""
    # return [1481, 1317, 1664, 2294, 1938, 1829, 3212, 2641, 2194, 1771, 1678, 1713]

    print("Please enter the monthly kWh (whole numbers only) consumption for:")

    monthly = []
    for i in range(1, 13):
        monthly.append(int(round(float(input(f"\t{MONTHS_MAP[i]}: ")), 0)))

    return monthly


class Consumption:

    def __init__(self, cons_monthly: List):

        self.cons_monthly = cons_monthly
        self.cons_annual = self.get_clean_annual(annual=sum(self.cons_monthly))
        self.cons_obj: Dict

    def __repr__(self):
        return (
            f"Consumption:\n"
            + f"\tannual consumption = {self.cons_annual}\n"
            + f"\tmonthly consumption = {self.cons_monthly}"
        )

    # IMPORT FROM UTILS
    @staticmethod
    def get_clean_annual(annual: int) -> AnyStr:
        """Convert the float ac_annual figure to a string with 2 decimal places"""
        return str(round(annual, 2))


if __name__ == "__main__":
    # path = r"/Users/nicolaaspjedema/Desktop/SolarCalculator/samples/sample_consumption.xlsx"
    monthly = manual_input_consumption()
    print(Consumption(monthly))