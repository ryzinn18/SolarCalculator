# tests.test_results.test_results.py
from backend.results import _get_graph, get_results, Results
from samples.sample_data_objects import *
from os.path import exists
from os import PathLike


def test__get_graph():
    """
    GIVEN Valid InputData and SolarPotential objects.
    WHEN _get_graph() is called with the above objects, it should generate a .png file at the specified path.
    THEN The Results object will be returned and Results.graph_path will exist.
    """
    test_result = _get_graph(
        input_data=SAMPLE_INPUT_DATA,
        solar_potential_data=SAMPLE_SOLAR_POTENTIAL_DATA,
        out_relative_path=SAMPLE_OUT_RELATIVE_PATH
    )
    assert isinstance(test_result, PathLike)
    assert exists(test_result)


def test_get_results():
    """
    GIVEN Valid InputData and SolarPotential objects.
    WHEN get_results() is called it will return a Results object.
    THEN A graph .png file exists.
    """
    test_result = get_results(
        input_data=SAMPLE_INPUT_DATA,
        solar_potential_data=SAMPLE_SOLAR_POTENTIAL_DATA
    )
    assert isinstance(test_result, Results)
    assert exists(test_result.graph_path)
