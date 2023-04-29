from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user

import threading
from datetime import datetime as dt
from decimal import Decimal

from .initialize_inputs import *
from src.utils.utils import MONTHS_MAP, clean_name, import_json, get_item_from_dynamodb

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


@views.route("/inputs/validate/")
def validate():
    """Validate inputs"""

    # Create time stamp for uid
    time_stamp = dt.now().__str__().replace(' ', '_').replace(':', '.')
    # Define input request parameters
    username = clean_name(request.args.get("name"))
    address = request.args.get("address")
    rating = request.args.get("rating")
    energy_monthly = request.args.get("energy").split(",")
    cost_monthly = request.args.get("cost").split(",")
    # Validate inputs
    if not validate_init_data(username, address, rating, energy_monthly, cost_monthly):
        # RETURN ERRANT JSON
        return redirect(url_for("views.home", user=current_user))
    # Define uid
    uid = f"{username}-{time_stamp}"
    # Transform to correct data types
    rating = round(float(rating), 2)
    energy_monthly = [int(n) for n in energy_monthly]
    cost_monthly = [float(n) for n in cost_monthly]
    # Calculate annual figures
    energy_annual = sum(energy_monthly)
    cost_annual = round(sum(cost_monthly))

    # Create init data item
    init_data = {
        "uid": uid,
        "name": username,
        "time_stamp": time_stamp,
        "address": address,
        "rating": Decimal(str(rating)),
        "energy_monthly": energy_monthly,
        "cost_monthly": [Decimal(str(n)) for n in cost_monthly],
        "energy_annual": energy_annual,
        "cost_annual": cost_annual,
        "state": None,
        "state_price": None,
        "capacity": None,
        "mod_quantity": None,
        "total_price": None,
        "tax_credit": None,
        "discount_price": None,
        "status": {
            "status_code": 200,
            "message": "Validation steps completed."
        },
    }

    response = store_inputs(table_name='sc-inputs', table_item=init_data)
    if not check_http_response(response_code=response.get('status').get('status_code')):
        return jsonify(response)
    else:
        return jsonify(init_data)


@views.route("/get-solar/")
def get_solar():
    """"""
    uid = request.args.get('uid')
    address = request.args.get('address')
    capacity = float(request.args.get('capacity'))

    # Call Lambda sc-be-solar for init solar data
    solar_inputs = {
        "uid": uid,
        "address": address,
        "capacity": capacity
    }
    init_solar_data = get_solar_data(solar_inputs)
    if not init_solar_data:
        return jsonify({"status": {"status_code": 442, "message": "Unable to retrieve Solar data."}})

    solar_data = {
        "uid": uid,
        "address": address,
        "capacity": capacity,
        "output_monthly": init_solar_data.get('output_monthly'),
        "output_annual": init_solar_data.get('output_annual'),
        "status": {
            "status_code": 200,
            "message": "Solar data retrieved successfully."
        }
    }

    return jsonify(solar_data)



