# backend.utils.py
from pydantic import conlist, PositiveInt, PositiveFloat
from typing import Union, Dict, Any, List, Type, TypeVar, Callable


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
AmbiguousListMonthly = conlist(item_type=float, min_items=12, max_items=12)
PandasDataFrame = TypeVar('PandasDataFrame')
JSON = Union[Dict[str, Any], List[Any], int, str, float, bool, Type[None]]


def get_root(parent_name: str) -> str:
    """Returns the path of the parent directory."""
    from os.path import isdir
    from pathlib import Path

    # Gets parent path via calling Path().parent and converts it to string via __str__()
    # Then strips the string at the parent directory and finally appends name to the path
    root = Path(__file__).parent.parent.__str__().split(parent_name)[0] + parent_name
    # Raises OSError if the resulting root path does not exist
    if not isdir(root):
        raise OSError(
            f'The following root directory at specified parent_name does not exist:\n\t{root}'
        )

    return root


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


def import_json(path: str) -> dict:
    """Imports a .json file and returns that object as a json (dict)"""
    from os.path import isfile
    from json import load as j_load

    # Raise OSError if the .json does not exist
    if not isfile(path):
        raise OSError(
            f'The following target_directory does not exist:\n\t{path}'
        )
    # Raise OSError if the file path passed is not a .json
    if not path.endswith('.json'):
        raise OSError(
            f'The path provided is a file that is not a .json\n\t{path.split(r"/")[-1]}'
        )

    # Create the json object
    with open(path, 'r') as j:
        obj = j_load(j)

    return obj


def export_json(j_obj: JSON, target_directory: str, out_name: str) -> None:
    """Exports Pydantic model to json file in target_directory"""
    from os.path import isdir

    # Remove the / from the end of the target_directory if it exists.
    target_directory = target_directory.rstrip(r'/')
    # Raise OSError if the target_directory does not exist
    if not isdir(target_directory):
        raise OSError(
            f'The following target_directory does not exist:\n\t{target_directory}'
        )

    # Write the model passed to a .json at specified location
    with open(fr'{target_directory}/{out_name}.json', 'w') as out:
        out.write(j_obj)


if __name__ == '__main__':
    print(import_json(r'/Users/ryanwright-zinniger/Desktop/SolarCalculator/src/samples/input.json'))
