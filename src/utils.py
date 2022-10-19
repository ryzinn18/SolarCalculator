"""
ToDo (smaller):
- Create uniform class (pydantic) for data objects.
- Figure out why git hub wont push on laptop.
- Import/interact with google sheets.

ToDo (large):
- Unit test all modules.
- Create web UI (JavaScript).
    - Build UI.
    - Build APIs.
- Top down documentation.
- Package!
"""

from typing import List, Dict

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


def round_list_elems(monthly: List[int]) -> List[int]:
    """Clean up the monthly list by converting to strings and rounding to 2 decimal spaces"""
    return [round(month) for month in monthly]


def get_out_obj(monthly: List[int], annual: int) -> Dict:
    """Generate an output object for the instance of the class"""
    out_obj = {
        'annual': annual,
        'monthly': monthly
    }
    for i, month in enumerate(monthly, 1):
        out_obj[i] = month

    return out_obj
