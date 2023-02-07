# SolarCalculator/src/utils.py
from src.config import google_api_sheet_id
from logging import getLogger, basicConfig, INFO
from typing import Union, Dict, Any, List, Type
from os.path import join
from pathlib import PurePath, Path

basicConfig(
    filename='logs/main.log',
    level=INFO,
    format='%(levelname)s:%(filename)s:%(asctime)s:%(funcName)s(): %(message)s',
    datefmt='%Y/%m/%d-%H.%M.%S',
    filemode='w',
)

LOGGER = getLogger(__name__ + '.utils')

JSON = Union[Dict[str, Any], List[Any], int, str, float, bool, Type[None]]
ROOT = Path(__file__).parents[1]

SAMPLES = {
    'sheet': google_api_sheet_id,

    'csv_valid': join(ROOT, 'src/samples/consumption_valid.csv'),
    'csv_invalid': join(ROOT, 'src/samples/consumption_invalid.csv'),

    'xlsx_valid': join(ROOT, 'src/samples/consumption_valid.xlsx'),

    'input_valid': join(ROOT, 'src/samples/input_valid.json'),
    'input_invalid_type': join(ROOT, 'src/samples/input_invalid_type.json'),
    'input_invalid_value': join(ROOT, 'src/samples/input_invalid_value.json'),

    'event_valid_form': join(ROOT, 'src/samples/event_valid_form.json'),
    'event_valid_csv': join(ROOT, 'src/samples/event_valid_csv.json'),
    'event_valid_xlsx': join(ROOT, 'src/samples/event_valid_xlsx.json'),
    'event_valid_sheet': join(ROOT, 'src/samples/event_valid_sheet.json'),

    'solar_potential_valid': join(ROOT, 'src/samples/solar_potential_valid.json'),

    'results_valid': join(ROOT, 'src/samples/results_valid.json'),

    'out': PurePath(join(ROOT, 'src/OutputGraphs/RyanZinniger-SolarGraph.png')),
}


def import_json(path: str) -> dict:
    """
    Imports a .json file and returns that object as a json (dict)
    :param path: A relative path to the existing json file. Must include .json in the end of the string
    :return A json (dict) object
    """

    from os.path import isfile
    from json import load as j_load

    LOGGER.info(f'Attempting to import the following json: {path}')

    # Raise OSError if the .json does not exist
    if not isfile(path):
        # LOGGER.error(f'The json specified at the following path does not exist: {path}')
        raise OSError(
            f'The following path to a file does not exist:\n\t{path}'
        )
    # Raise OSError if the file path passed is not a .json
    if not path.endswith('.json'):
        # LOGGER.error(f'The path specified is not to a .json file: {path}')
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

    # LOGGER.info(f'Attempting to export the following object to target_directory: {target_directory}')
    # LOGGER.info(j_obj)

    # Clean up variables passed
    target_directory = target_directory.rstrip(r'/')
    out_name = out_name.rstrip('.json')
    # Raise OSError if the target_directory does not exist
    if not isdir(target_directory):
        # LOGGER.error(f'The target directory specified does not exist: {target_directory}')
        raise OSError(
            f'The following target_directory does not exist:\n\t{target_directory}'
        )

    output = fr'{target_directory}/{out_name}.json'
    # Write the model passed to a .json at specified location
    with open(output, 'w') as out:
        out.write(j_obj)

    # LOGGER.info(f'The json file was successfully exported: {output}')


if __name__ == '__main__':
    print(import_json(SAMPLES['input_valid']))
