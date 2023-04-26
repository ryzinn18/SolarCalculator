from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user

from datetime import datetime as dt

from .initialize_inputs import *
from .utils import MONTHS_MAP, clean_name

views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
def home():
    """Home view."""

    return render_template("home.html", user=current_user, months=MONTHS_MAP.values())


@views.route("/documentation")
def documentation():
    """Documentation view."""

    return render_template("docs.html", user=current_user)


@views.route("/init-tool", methods=["GET", "POST"])
def init_data():
    """Initialize the Solar Calculator tool."""

    # Edge Case - return to create post page if method is not POST
    if request.method != "POST":
        return render_template("home.html", user=current_user)

    # Define request parameters from input form
    time_stamp = dt.now().__str__().replace(' ', '_').replace(':', '.')
    username = clean_name(request.form.get("name"))
    uid = f"{username}-{time_stamp}"
    address = request.form.get("address")
    mod_data = {
        "mod_kwh": request.form.get("mod_kwh"),
        "mod_price": request.form.get("mod_price"),
    }
    monthly_data = {
        # Key=month (str): Value=[energyMonth, costMonth] (array[int, float])
    }
    for month in MONTHS_MAP.values():
        monthly_data[month] = [str(request.form.get(f"energy{month}")), str(request.form.get(f"cost{month}"))]

    # Validate Input Data
    if not validate_init_data(username, address, mod_data, monthly_data):
        return redirect(url_for("views.home", user=current_user))

    # Call Lambda sc-be-solar for solar data
    init_inputs = {
        "uid": uid,
        "address": address,
        "capacity": 1
    }
    solar_init_data = get_solar_data(init_inputs)
    if not solar_init_data:
        return redirect(url_for("views.home", user=current_user))

    # Calculate capacity and mod_quantity
    capacity = suggest_capacity(monthly_data=monthly_data, annual_output=solar_init_data.get('output_annual'))
    # noinspection PyTypeChecker
    mod_quantity = suggest_mod_quantity(capacity=capacity, mod_rating=mod_data.get('mod_kwh'))

    # Store validated input data - async
    store_inputs(
        username=username,
        time_stamp=time_stamp,
        address=address,
        monthly_data=monthly_data,
        capacity=capacity,
        mod_data=mod_data
    )

    init_data = {
        "uid": uid,
        "suggested_capacity": capacity,
        "suggested_mod_quantity": mod_quantity,
    }

    """Write code to pass init_data to home page, expand the init_data section, and call get_results."""


    # return render_template("output.html", user=current_user, output=results, months=MONTHS_MAP)