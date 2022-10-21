"""
ToDo (smaller):
- Add cost/value to data objects
- Create uniform class (pydantic) for data objects.

ToDo (large):
- Unit test all modules.
- Create web UI (JavaScript).
    - Build UI.
    - Build APIs.
- Top down documentation.
- Package!
"""

from pydantic import BaseModel
from typing import List, Dict, Literal, AnyStr

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


class Energy(BaseModel):
    # Required
    name: AnyStr
    obj_type: Literal['consumption', 'iridescence']
    monthly_energy_data: List[int]
    annual_energy_data: int
    monthly_cost_data: List[float]
    annual_cost_data: float
    # Optional
    units = 'kiloWattHours'
    months_int = sorted(MONTHS_MAP.keys())
    months_str = [MONTHS_MAP[n] for n in months_int]


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
