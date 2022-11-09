# backend.utils.py
from pydantic import conlist, PositiveInt
from os import PathLike


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


def get_absolute_path(relative_path: PathLike[str]) -> PathLike[str]:
    """Pass this function a relative path and get the absolute path based on cwd."""
    from os import getcwd
    from os.path import join
    from pathlib import PurePath

    return PurePath(join(getcwd(), relative_path))


if __name__ == '__main__':
    pass
