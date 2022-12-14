# tests.test_inputs.py
from pytest import raises as p_raises
from utils import import_json, SAMPLES
from backend import input_csv, input_xlsx, input_sheets, \
    input_handler, InputData, InputError
from backend.inputs import _validate_mod_kwh, _calculate_cost_per_kwh


_INPUT_VALID = import_json(SAMPLES['input_valid'])
_INPUT_INVALID = import_json(SAMPLES['input_invalid_value'])


def test_validate():
    """
    NOTE: validate() is a decorator for the input function

    GIVEN An input function (e.g., input_csv()) being called with the @validate decorator
    WHEN An invalid input is given
    THEN The appropriate exception should be thrown
    """
    with p_raises(FileNotFoundError):
        input_csv(file_path=r'./fail/fail.csv')
    with p_raises(ValueError):
        input_csv(file_path=SAMPLES['csv_invalid'])


def test__validate_mod_kwh():
    """
    GIVEN A string representing users mod_kwh which can be converted to a float.
    WHEN The _validate_mod_kwh() is called on that string.
    THEN _validate_mod_kwh() returns a float object.
    """
    # Assert correct functionality
    assert _validate_mod_kwh(in_data='0.4') == 0.4
    assert isinstance(_validate_mod_kwh(in_data='0.4'), float)
    # Invalid type is passed (non-numeric string)
    with p_raises(ValueError):
        _validate_mod_kwh(in_data='fail')
    # Invalid numeric value is passed (0 >= invalid value > 1.5)
    with p_raises(ValueError):
        _validate_mod_kwh(in_data='1.8')
    with p_raises(ValueError):
        _validate_mod_kwh(in_data='0')
    with p_raises(ValueError):
        _validate_mod_kwh(in_data='-1')


def test__calculate_cost_per_kwh():
    """
    GIVEN ListMonthly (see backend/utils.py) lists for cost and consumption
    WHEN _calculate_cost_per_kwh() is called on 2 ListMonthly lists the average cost/kWh is calculated
    THEN _calculate_cost_per_kwh() returns a valid float object
    """

    assert _calculate_cost_per_kwh(
                cost=_INPUT_VALID['cost_monthly'], consumption=_INPUT_VALID['consumption_monthly']
            ) == _INPUT_VALID['cost_per_kwh']
    assert _calculate_cost_per_kwh(
                cost=_INPUT_INVALID['cost_monthly'], consumption=_INPUT_INVALID['consumption_monthly']
            ) == _INPUT_VALID['cost_per_kwh']


def test_input_csv():
    """
    GIVEN A valid relative path to a valid .csv file
    WHEN The input_csv() function is called
    THEN input_csv() returns a InputData object with valid values
    """
    test_output = input_csv(file_path=SAMPLES['csv_valid'])
    # Assert the correct object is returned. This validates data types/structures.
    assert isinstance(test_output, InputData)
    # Assert valid values are reported/calculated
    assert test_output.consumption_monthly == _INPUT_VALID['consumption_monthly']
    assert test_output.consumption_annual == _INPUT_VALID['consumption_annual']
    assert test_output.cost_monthly == _INPUT_VALID['cost_monthly']
    assert test_output.cost_annual == _INPUT_VALID['cost_annual']
    assert test_output.cost_per_kwh == _INPUT_VALID['cost_per_kwh']


def test_input_xlsx():
    """
    GIVEN A valid relative path to valid a .xlsx file
    WHEN The input_xlsx() function is called
    THEN input_xlsx() returns a InputData object with valid values
    """
    test_output = input_xlsx(file_path=SAMPLES['xlsx_valid'])
    # Assert the correct object is returned. This validates data types/structures.
    assert isinstance(test_output, InputData)
    # Assert valid values are reported/calculated
    assert test_output.consumption_monthly == _INPUT_VALID['consumption_monthly']
    assert test_output.consumption_annual == _INPUT_VALID['consumption_annual']
    assert test_output.cost_monthly == _INPUT_VALID['cost_monthly']
    assert test_output.cost_annual == _INPUT_VALID['cost_annual']
    assert test_output.cost_per_kwh == _INPUT_VALID['cost_per_kwh']


def test_input_sheets():
    """
    GIVEN A valid relative path to valid a .sheet file
    WHEN The input_sheets() function is called
    THEN input_sheets() returns a InputData object with valid values
    """
    test_output = input_sheets(sheet_id=SAMPLES['sheet'])
    # Assert the correct object is returned. This validates data types/structures.
    assert isinstance(test_output, InputData)
    # Assert valid values are reported/calculated
    assert test_output.consumption_monthly == _INPUT_VALID['consumption_monthly']
    assert test_output.consumption_annual == _INPUT_VALID['consumption_annual']
    assert test_output.cost_monthly == _INPUT_VALID['cost_monthly']
    assert test_output.cost_annual == _INPUT_VALID['cost_annual']
    assert test_output.cost_per_kwh == _INPUT_VALID['cost_per_kwh']


def test_input_handler():
    """
    GIVEN A correct keyword argument and input source for input_handler().
    WHEN The handler function is executed with correct inputs.
    THEN Calls the correct corresponding function and returns a InputData object
    """
    # Assert that when passed valid inputs, the handler returns a InputData object
    assert isinstance(input_handler(input_type='csv', input_source=SAMPLES['csv_valid']), InputData)
    assert isinstance(input_handler(input_type='xlsx', input_source=SAMPLES['xlsx_valid']), InputData)
    assert isinstance(input_handler(input_type='sheet', input_source=SAMPLES['sheet']), InputData)
    # Assert that the accepted input types are recognized
    assert ['csv', 'xlsx', 'sheet'] == InputError.valid_input_types
    # Assert that InputError is passed when an invalid kw arg for input_type is passed.
    with p_raises(InputError):
        input_handler(input_type='fail', input_source=SAMPLES['csv_valid'])

