from flask import flash

from typing import Callable


def validate(function: Callable) -> Callable:
    """Decorator function for handling exceptions when validating input data."""

    def wrapper_validate(*args, **kwargs):
        """Wraps function call in a try/except clause to catch FileNotFound, ValueError and general Exceptions"""
        try:
            function(*args, **kwargs)
        except TypeError:
            # Log error
            flash(
                "You submitted a blank value. Ensure no input fields are blank and rerun this tool.",
                category="error"
            )
            return False
        except ValueError:
            # Log error
            flash(
                "You entered an incorrect value. Ensure all inputs except Name and Address are numbers.",
                category="error"
            )
            return False
        else:
            return True

    return wrapper_validate


@validate
def _validate_energy_init_data(energy_data: list) -> None:
    """Validate that the data used to passed for initialization is correct."""

    for i in range(12):
        int(energy_data[i])


@validate
def _validate_energy_init_data(cost_data: list) -> None:
    """Validate that the data used to passed for initialization is correct."""

    for i in range(12):
        float(cost_data[i])


@validate
def _validate_rating_init_data(rating: str) -> None:
    """Validate that the data used to passed for initialization is correct."""

    float(rating)


@validate
def _validate_string_init_data(data: str) -> None:
    """Validate that the Name and Address fields are not null or NoneType."""
    if not data:
        raise TypeError


def validate_init_data(username: str, address: str, rating: str, energy_data: list, cost_data: list) -> bool:
    """Validate data passed & update data types in-place for mod_data & monthly_data."""
    name_validated = _validate_string_init_data(username)
    address_validated = _validate_string_init_data(address)
    rating_validated = _validate_rating_init_data(rating)
    energy_validated = _validate_energy_init_data(energy_data)
    cost_validated = _validate_energy_init_data(cost_data)

    return True if (name_validated and address_validated and rating_validated and energy_validated and cost_validated) \
        else False


if __name__ == "__main__":
    # TEST VALIDATION
    # monthly = {
    #     "January": ["300", "300"],
    #     "February": ["100", "300"],
    #     "March": ["100", "300"],
    #     "April": ["100", "300"],
    #     "May": ["100", "300"],
    #     "June": ["100", "300"],
    #     "July": ["100", "300"],
    #     "August": ["100", "300"],
    #     "September": ["100", "300"],
    #     "October": ["100", "300"],
    #     "November": ["100", "300"],
    #     "December": ["100", "300"],
    # }
    # mod = {
    #     'mod_kwh': "0.4",
    #     "mod_price": "200"
    # }
    # print(
    #     validate_init_data(
    #         username="Ryan",
    #         address="123 Ocean Street",
    #         mod_data=mod,
    #         monthly_data=monthly
    #     )
    # )
    # print(type(mod['mod_price']))
    pass
