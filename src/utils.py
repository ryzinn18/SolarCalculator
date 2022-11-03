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
from typing import Any, List, Dict, Optional, AnyStr, Literal

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


class Metrics(BaseModel):
    # Required
    name: AnyStr
    obj_type: Literal['cost', 'consumption', 'iridescence']
    data_monthly: conlist(PositiveInt, min_items=12, max_items=12)
    data_annual: PositiveInt
    units: Literal['kiloWattHours', 'dollars']
    # Optional
    note: Optional[str]


if __name__ == '__main__':
    pass
