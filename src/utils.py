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
from pydantic import BaseModel, conlist, PositiveInt
from typing import List, Dict, Optional, AnyStr, Literal

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


def round_list_elems(l: List[int]) -> List[int]:
    """Clean up the monthly list by converting to strings and rounding to 2 decimal spaces"""
    return [round(elem) for elem in l]


def get_out_obj(monthly: List[int], annual: int) -> Dict:
    """Generate an output object for the instance of the class"""
    out_obj = {
        'annual': annual,
        'monthly': monthly
    }
    for i, month in enumerate(monthly, 1):
        out_obj[i] = month

    return out_obj


class Metrics(BaseModel):
    # Required
    name: AnyStr
    obj_type: Literal['cost', 'consumption', 'iridescence']
    data_monthly: conlist(PositiveInt, min_items=12, max_items=12)
    data_annual: PositiveInt
    units: str
    # Optional
    note: Optional[str]


class Data(Metrics):
    def __init__(self, metrics: Metrics):
        self.months_int = MONTHS_MAP.keys()
        self.months_str = [MONTHS_MAP[n] for n in self.months_int]
        self.data_object = get_out_obj(monthly=metrics.data_monthly, annual=metrics.data_annual)


if __name__ == '__main__':
    a = "test"
    print(a.title())