# backend.utils.py
from pydantic import conlist, PositiveInt, PositiveFloat
from typing import Callable


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

IntListMonthly = conlist(item_type=PositiveInt, min_items=12, max_items=12)
FloatListMonthly = conlist(item_type=PositiveFloat, min_items=12, max_items=12)


def validate_data(function: Callable) -> Callable:
    """Decorator function for ensuring that a call to create a BaseModel object completes."""
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)

        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"The file specified at the below location does not exist:\n"
                + f"\t{e.filename}\n"
                + "Please update the file path and try again."
            )
        except ValueError:
            raise ValueError(
                f"One or more of the values entered are invalid.\n"
                + "Please review the values entered and try again."
            )

    return wrapper


if __name__ == '__main__':
    pass
