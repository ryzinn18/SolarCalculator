# SolarCalculator/src/backend/utils.py
from pydantic import conlist, PositiveInt, PositiveFloat
from typing import TypeVar

# Dictionary containing the month numbers (keys - int) and months spelled (values - str)
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

# Custom types for pydantic objects and type-hinting
IntListMonthly = conlist(item_type=PositiveInt, min_items=12, max_items=12)
FloatListMonthly = conlist(item_type=PositiveFloat, min_items=12, max_items=12)
AmbiguousListMonthly = conlist(item_type=float, min_items=12, max_items=12)
PandasDataFrame = TypeVar('PandasDataFrame')


if __name__ == '__main__':
    pass
