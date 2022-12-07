# backend.utils.py
from pydantic import conlist, PositiveInt, PositiveFloat
import logging
from typing import Union, Dict, Any, List, Type, TypeVar, Callable

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

_backend_log_file_name = './logs/backend.log'
logging.basicConfig(level=logging.DEBUG, filename=_backend_log_file_name, filemode='w',
                    format='%(name)s - %(filename)s - %(levelname)s[%(funcName)s()]: %(message)s')
LOGGER = logging.getLogger(__name__)
"""LOGGER.setLevel(logging.INFO)
_file_handler = logging.FileHandler(_backend_log_file_name)
_file_handler.setFormatter(logging.Formatter('%(name)s - %(filename)s - %(levelname)s[%(funcName)s()]: %(message)s'))
_file_handler.setLevel(logging.INFO)
LOGGER.addHandler(_file_handler)"""


# Custom types for pydantic objects and type-hinting
IntListMonthly = conlist(item_type=PositiveInt, min_items=12, max_items=12)
FloatListMonthly = conlist(item_type=PositiveFloat, min_items=12, max_items=12)
AmbiguousListMonthly = conlist(item_type=float, min_items=12, max_items=12)
PandasDataFrame = TypeVar('PandasDataFrame')
JSON = Union[Dict[str, Any], List[Any], int, str, float, bool, Type[None]]


def get_root(root_name: str) -> str:
    """Returns the path of the parent directory."""
    from os.path import isdir
    from pathlib import Path

    LOGGER.info(f'Attempting get_root(parent_name={root_name})')
    # Gets parent path via calling Path().parent and converts it to string via __str__()
    # Then strips the string at the parent directory and finally appends name to the path
    root = Path(__file__).parent.parent.__str__().split(root_name)[0] + root_name
    # Raises OSError if the resulting root path does not exist
    if not isdir(root):
        LOGGER.exception(f'Root directory found is not a directory: {root}')
        raise OSError(
            f'The following root directory at specified parent_name does not exist:\n\t{root}'
        )

    LOGGER.info(f'get_root() found the following directory to be the root: {root}')
    return root


def validate_data(function: Callable) -> Callable:
    """Decorator function for ensuring that a call to create a BaseModel object completes."""

    def wrapper_validate_data(*args, **kwargs):
        LOGGER.info('Validating input data.')
        try:
            result = function(*args, **kwargs)
        except FileNotFoundError as e:
            LOGGER.exception(f'The file specified does not exist.', exc_info=True)
            raise FileNotFoundError(
                f"The file specified at the below location does not exist:\n"
                + f"\t{e.filename}\n"
                + "Please update the file path and try again."
            )
        except ValueError:
            LOGGER.exception(f'The input data could not be validated.', exc_info=True)
            raise ValueError(
                f"One or more of the values entered are invalid.\n"
                + "Please review the values entered and try again."
            )
        else:
            LOGGER.info('Input data successfully validated.')
            return result

    return wrapper_validate_data


def import_json(path: str) -> dict:
    """Imports a .json file and returns that object as a json (dict)"""
    from os.path import isfile
    from json import load as j_load

    # Raise OSError if the .json does not exist
    if not isfile(path):
        LOGGER.exception(f'The json specified at the following path does not exist: {path}')
        raise OSError(
            f'The following path to a file does not exist:\n\t{path}'
        )
    # Raise OSError if the file path passed is not a .json
    if not path.endswith('.json'):
        LOGGER.exception(f'The path specified is not to a .json file: {path}')
        raise OSError(
            f'The path provided is a file that is not a .json\n\t{path.split(r"/")[-1]}'
        )

    # Create the json object
    with open(path, 'r') as j:
        obj = j_load(j)
        LOGGER.info(f'The following json file successfully imported: {path}')

    return obj


def export_json(j_obj: JSON, target_directory: str, out_name: str) -> None:
    """Exports Pydantic model to json file in target_directory"""
    from os.path import isdir

    # Clean up variables passed
    target_directory = target_directory.rstrip(r'/')
    out_name = out_name.rstrip('.json')
    # Raise OSError if the target_directory does not exist
    if not isdir(target_directory):
        LOGGER.exception(f'The target directory specified does not exist: {target_directory}')
        raise OSError(
            f'The following target_directory does not exist:\n\t{target_directory}'
        )

    # Write the model passed to a .json at specified location
    with open(fr'{target_directory}/{out_name}.json', 'w') as out:
        out.write(j_obj)
        LOGGER.info(f'The json file was successfully exported.')


if __name__ == '__main__':
    import_json('dne')