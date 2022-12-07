# ~/src/utils.py
import logging
from typing import Union, Dict, Any, List, Type
from pathlib import PurePath

JSON = Union[Dict[str, Any], List[Any], int, str, float, bool, Type[None]]

SAMPLES = {
    'sheet': '1gneTmzTrGTsJIrjkjzEOYS-Bq7irB_WZ2TJWXMlFp4k',
    'csv_valid': r'./samples/consumption_valid.csv',
    'xlsx_valid': r'./samples/consumption_valid.xlsx',

    'input_valid': r'./samples/input_valid.json',
    'input_invalid_type': r'./samples/input_invalid_type.json',
    'input_invalid_value': r'./samples/input_invalid_value.json',

    'out': PurePath(fr"./OutputGraphs/RyanZinniger-SolarGraph.png"),
}


def create_logger(file_name: str) -> logging.Logger:
    """Abstracted method for creating Logger objects."""
    file_path = f'./logs/{file_name}.log'
    log_format = '%(name)s - %(filename)s - %(levelname)s[%(funcName)s()]: %(message)s'

    logging.basicConfig(
        level=logging.INFO,
        filename=file_path,
        filemode='w',
        format=log_format
    )
    return logging.getLogger(__name__)


def import_json(path: str) -> dict:
    """
    Imports a .json file and returns that object as a json (dict)
    :param path: A relative path to the existing json file. Must include .json in the end of the string
    :return A json (dict) object"""
    from os.path import isfile
    from json import load as j_load

    # Raise OSError if the .json does not exist
    if not isfile(path):
        LOGGER.error(f'The json specified at the following path does not exist: {path}')
        raise OSError(
            f'The following path to a file does not exist:\n\t{path}'
        )
    # Raise OSError if the file path passed is not a .json
    if not path.endswith('.json'):
        LOGGER.error(f'The path specified is not to a .json file: {path}')
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
        LOGGER.error(f'The target directory specified does not exist: {target_directory}')
        raise OSError(
            f'The following target_directory does not exist:\n\t{target_directory}'
        )

    # Write the model passed to a .json at specified location
    with open(fr'{target_directory}/{out_name}.json', 'w') as out:
        out.write(j_obj)
        LOGGER.info(f'The json file was successfully exported.')


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
        LOGGER.error(f'Root directory found is not a directory: {root}')
        raise OSError(
            f'The following root directory at specified parent_name does not exist:\n\t{root}'
        )

    LOGGER.info(f'get_root() found the following directory to be the root: {root}')
    return root


LOGGER = create_logger(file_name='src')


if __name__ == '__main__':
    pass
