from pydantic import BaseModel, conlist, PositiveInt
from typing import Optional, AnyStr, Literal

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

ListMonthly = conlist(item_type=PositiveInt, min_items=12, max_items=12)


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
