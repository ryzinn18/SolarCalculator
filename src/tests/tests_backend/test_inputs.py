# tests.test_inputs.py
from utils import import_json, SAMPLES
from backend.inputs import input_csv, input_xlsx, _calculate_cost_per_kwh, \
    _validate_mod_kwh, input_handler, InputError, InputData

def test__calculate_cost_per_kwh():
    """
    GIVEN A ListMonthly (see backend.utils) list for cost and consumption, \
        accurately calculate the average cost/kwh.
    WHEN _calculate_cost_per_kwh is called on 2 ListMonthly lists.
    THEN _calculate_cost_per_kwh() returns a positive float object.
    """
    json_invalid_value = import_json(SAMPLES['input_invalid_value'])
    json_invalid_type = import_json(SAMPLES['input_invalid_type'])

    cost_invalid_value = json_invalid_value['cost_monthly']
    cost_invalid_type = json_invalid_type['cost_monthly']

    """
    Need to test that:
    - Fails correctly based on values and types
        - String instead of numeric
        - Negative when should be positive
    - Calculates correctly when valid values given
    """

    # both test lists are the same so the result should be 1
    test_result_value = _calculate_cost_per_kwh(cost=invalid_cost, consumption=test_consumption)

    assert isinstance(test_result, float)
    assert test_result == 1
    assert test_result > 0


def test__validate_mod_kwh():
    """
    GIVEN A string representing users mod_kwh which can be converted to a float.
    WHEN The _validate_mod_kwh() is called on that string.
    THEN _validate_mod_kwh() returns a float object.
    """
    assert isinstance(_validate_mod_kwh(in_data="0.10"), float)


def test_input_csv():
    """
    GIVEN A valid relative path to a .csv file.
    WHEN The input_csv() function is called.
    THEN input_csv() returns a InputData object
    """
    assert isinstance(input_csv(file_path=SAMPLE_CSV), InputData)


def test_input_xlsx():
    """
    GIVEN A valid relative path to a .csv file.
    WHEN The input_csv() function is called.
    THEN input_csv() returns a InputData object
    """
    assert isinstance(input_xlsx(file_path=SAMPLE_XLSX), InputData)


def test_input_sheets():
    """"""
    pass


def test_inputs_handler():
    """
    GIVEN A correct keyword argument and input source for input_handler().
    WHEN The handler function is executed with correct inputs.
    THEN Calls the correct corresponding function and returns a InputData object
    """
    assert isinstance(input_handler(input_type='csv', input_source=SAMPLE_CSV), InputData)
    assert isinstance(input_handler(input_type='xlsx', input_source=SAMPLE_XLSX), InputData)
    # assert isinstance(input_handler(input_type='sheet', input_source=SAMPLE_SHEET), InputData)

    assert ['csv', 'xlsx', 'sheet', 'manual'] == InputError.valid_input_types
    assert 'wrong' not in InputError.valid_input_types
