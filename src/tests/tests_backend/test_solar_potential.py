# tests.test_solar_potential.py
from backend.solar_potential import _get_params, _get_iridescence_obj, \
    get_solar_potential, SolarPotentialData
from samples.sample_data_objects import SAMPLE_INPUT_DATA


def test__get_params():
    """
    GIVEN The appropriate arguments to create a params object.
    WHEN _get_params() is called.
    THEN A dictionary with 7 items - all of which are strings - is returned.
    """
    test_params = _get_params(capacity=1, address=SAMPLE_INPUT_DATA.address)
    assert isinstance(test_params, dict)
    assert len(test_params) == 7
    for elem in test_params:
        assert isinstance(elem, str)


def test__get_iridescence_object():
    """
    GIVEN Valid parameters and token for PVWatts api.
    WHEN Calling the api via the requests library.
    THEN Get a dictionary containing the response.
    """
    test_params = _get_params(capacity=1, address=SAMPLE_INPUT_DATA.address)
    test_irid_obj = _get_iridescence_obj(params=test_params)

    assert isinstance(test_irid_obj, dict)
    assert test_irid_obj.get('outputs') is not None
    assert len(test_irid_obj) == 7


def test_get_solar_potential():
    """
    GIVEN Valid parameters for creating an instance of the SolarPotentialData object.
    WHEN Calling the get_solar_potential() function.
    THEN Get a valid SolarPotentialData object.
    """
    assert isinstance(
        get_solar_potential(
            address=SAMPLE_INPUT_DATA.address,
            annual_consumption=SAMPLE_INPUT_DATA.consumption_annual
        ),
        SolarPotentialData
    )


if __name__ == '__main__':
    pass
