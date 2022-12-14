# tests.test_results.py
from utils import import_json, SAMPLES
from backend import input_handler, get_solar_potential, get_data_df, create_comparison_graph, create_out_csv, \
    get_results, Results
from backend.results import _average
from pandas import DataFrame
from os.path import isfile, join as os_join
from tempfile import TemporaryDirectory

_INPUT_VALID = import_json(SAMPLES['input_valid'])
_INPUT_INVALID = import_json(SAMPLES['input_invalid_value'])
_SOLAR_POTENTIAL_VALID = import_json(SAMPLES['solar_potential_valid'])
_RESULT_VALID = import_json(SAMPLES['results_valid'])

_MODEL_INPUT = input_handler(input_type='csv', input_source=SAMPLES['csv_valid'])
_MODEL_SOLAR = get_solar_potential(address=_INPUT_VALID['address'], annual_consumption=_INPUT_VALID['consumption_annual'])

_TEST_DF = get_data_df(
    input_data=_MODEL_INPUT,
    solar_potential_monthly=_SOLAR_POTENTIAL_VALID['solar_potential_monthly'],
    potential_cost_monthly=_RESULT_VALID['potential_cost_monthly'],
    savings_monthly=_RESULT_VALID['savings_monthly'],
    cost_reduction_monthly=_RESULT_VALID['cost_reduction_monthly']
)


def test__average():
    """
    GIVEN An object that is a Sequence or Collection with numeric values
    WHEN _average() is called on that object
    THEN An average value is returned as an integer
    """
    assert _average(iterable=[1, 4, 7]) == 4


def test_get_data_df():
    """
    GIVEN Valid InputData, SolarPotentialData, and other pertinent data objects
    WHEN get_data_df() is called on those valid data objects
    THEN A Pandas DataFrame is returned
    """
    # Assert the output is a pandas DataFrame
    assert isinstance(_TEST_DF, DataFrame)
    # Assert the DataFrame has 13 rows
    assert len(_TEST_DF) == 13
    # Assert calculations done in the function are correct
    assert _TEST_DF.loc[12, 'Potential kWh'] == sum(_SOLAR_POTENTIAL_VALID['solar_potential_monthly'])
    assert _TEST_DF.loc[12, 'Cost Reduction %'] == _average(_RESULT_VALID['cost_reduction_monthly'])


def test_create_comparison_graph():
    """
    GIVEN The appropriate inputs to create a comparison graph
    WHEN The create_comparison_graph() is called given valid inputs
    THEN A comparison graph is created at designated location and saved as a .png file
    """
    # Create a temp dir and write a temp output graph to that dir, assert that the temp file is created
    with TemporaryDirectory() as tmp_dir:
        tmp_file_path = os_join(tmp_dir, 'TEST.png')
        create_comparison_graph(
            title='TEST',
            df1=_TEST_DF['Consumption kWh'],
            df2=_TEST_DF['Potential kWh'],
            label1='test',
            label2='test',
            y_label='test',
            out_path=tmp_file_path,
            graph_type='energy'
        )
        assert isfile(tmp_file_path)


def test_create_out_csv():
    """
    GIVEN Valid data objects header, data_df, and footer
    WHEN create_out_csv() is called
    THEN An output csv is created at out_relative_path
    """
    # Create a temp dir and write a temp output graph to that dir, assert that the temp file is created
    with TemporaryDirectory() as tmp_dir:
        tmp_file_path = os_join(tmp_dir, 'TEST.csv')
        create_out_csv(
            header={'Name': 'TEST',
                    'Address': 'test_address',
                    'Cost/kWh': 'test_cost/kWh',
                    '': ''},  # Blank Row
            data_df=_TEST_DF,
            footer={'': '',  # Blank Row
                    'Note:': 'test_note',
                    'Potential kWh Source:': 'test_source'},
            out_relative_path=tmp_file_path
        )
        assert isfile(tmp_file_path)


def test_get_results():
    """
    GIVEN Valid InputData and SolarPotentialData objects
    WHEN get_results() is called on those valid data objects
    THEN Return a valid ResultsData object
    """
    test_results = get_results(input_data=_MODEL_INPUT, solar_potential_data=_MODEL_SOLAR)

    assert isinstance(test_results, Results)
