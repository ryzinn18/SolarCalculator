# SolarCalculator/src/utils.py
from pydantic import BaseModel, conlist, PositiveInt, PositiveFloat, HttpUrl
from config import google_api_sheet_id
from logging import getLogger, basicConfig, INFO
from typing import Union, Dict, Any, List, Type, TypeVar
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

    'event_valid_form': join(ROOT, 'src/samples/event_inputs/input_form.json'),
    'event_valid_csv': join(ROOT, 'src/samples/event_inputs/input_csv.json'),
    'event_valid_xlsx': join(ROOT, 'src/samples/event_inputs/input_xlsx.json'),
    'event_valid_sheet': join(ROOT, 'src/samples/event_inputs/input_sheet.json'),
    'event_ready_for_solar': join(ROOT, 'src/samples/event_inputs/ready_forsolar.json'),
    'event_ready_for_results': join(ROOT, 'src/samples/event_inputs/ready_for_results.json'),

    'solar_potential_valid': join(ROOT, 'src/samples/solar_potential_valid.json'),

    'results_valid': join(ROOT, 'src/samples/results_valid.json'),

    'out': PurePath(join(ROOT, 'src/OutputGraphs/RyanZinniger-SolarGraph.png')),
}

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

# Custom types for pydantic objects and type-hinting
IntListMonthly = conlist(item_type=PositiveInt, min_items=12, max_items=12)
FloatListMonthly = conlist(item_type=PositiveFloat, min_items=12, max_items=12)
AmbiguousListMonthly = conlist(item_type=float, min_items=12, max_items=12)
PandasDataFrame = TypeVar('PandasDataFrame')


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

    LOGGER.info(f'Attempting to export the following object to target_directory: {target_directory}')
    LOGGER.info(j_obj)

    # Clean up variables passed
    target_directory = target_directory.rstrip(r'/')
    out_name = out_name.rstrip('.json')
    # Raise OSError if the target_directory does not exist
    if not isdir(target_directory):
        LOGGER.error(f'The target directory specified does not exist: {target_directory}')
        raise OSError(
            f'The following target_directory does not exist:\n\t{target_directory}'
        )

    output = fr'{target_directory}/{out_name}.json'
    # Write the model passed to a .json at specified location
    with open(output, 'w') as out:
        out.write(j_obj)

    LOGGER.info(f'The json file was successfully exported: {output}')


class InputData(BaseModel):
    # Required
    uid: str
    name: str
    address: str
    mod_kwh: PositiveFloat
    consumption_monthly: IntListMonthly
    consumption_annual: PositiveInt
    cost_monthly: FloatListMonthly
    cost_annual: PositiveFloat
    cost_per_kwh: PositiveFloat
    # Optional
    note: str = None
    # Default
    units_consumption = "kiloWattHours"
    units_cost = "Dollars"
    sym_consumption = "kWh"
    sym_cost = "$"


class EventReadyForSolar(BaseModel):
    uid: str
    input_data: InputData


class SolarPotentialData(BaseModel):
    # Required
    uid: str
    address: str
    solar_potential_monthly: IntListMonthly
    solar_potential_annual: PositiveInt
    needed_kwh: PositiveInt
    input_data: InputData
    # Default
    note = "Solar potential (kWh) reported over a 30 year average."
    source = "pvwatts.nrel.gov/pvwatts.php"
    units_solar_potential = "kiloWattHours"
    sym_solar_potential = "kWh"


class EventReadyForResults(BaseModel):
    uid: str
    input_data: InputData
    solar_data: SolarPotentialData


class Results(BaseModel):
    # Required
    uid: str
    name: str
    address: str
    actual_consumption_monthly: IntListMonthly
    actual_cost_monthly: FloatListMonthly
    potential_production_monthly: IntListMonthly
    potential_cost_monthly: AmbiguousListMonthly
    savings_monthly: FloatListMonthly
    cost_reduction_monthly: IntListMonthly
    cost_reduction_average: int
    mod_quantity: PositiveInt
    results_data_json: JSON
    uri_data_csv: str
    uri_graph_cost: str
    uri_graph_energy: str


class EventFinal(BaseModel):
    uid: str
    input_data: InputData
    solar_data: SolarPotentialData
    results_data: Results


if __name__ == '__main__':
    # print(import_json(SAMPLES['input_valid']))
    pass
