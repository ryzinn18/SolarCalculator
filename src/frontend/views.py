from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user

import threading
from datetime import datetime as dt
from decimal import Decimal

from .initialize_inputs import *
from .utils import MONTHS_MAP, clean_name, import_json

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


@views.route("/init-data/")
def init_tool():
    """Initialize the Solar Calculator tool."""

    print((request.args.get('energy').split(",")))

    # Define request parameters from request
    time_stamp = dt.now().__str__().replace(' ', '_').replace(':', '.')
    username = clean_name(request.args.get("name"))
    uid = f"{username}-{time_stamp}"
    address = request.args.get("address")
    rating = request.args.get("rating")
    energy_data = request.args.get("energy").split(",")
    cost_data = request.args.get("cost").split(",")
    # Validate Input Data
    if not validate_init_data(username, address, rating, energy_data, cost_data):
        # RETURN ERRANT JSON
        return redirect(url_for("views.home", user=current_user))
    rating = float(rating)
    energy_data = [int(n) for n in energy_data]
    cost_data = [float(n) for n in cost_data]

    # Call Lambda sc-be-solar for init solar data
    init_solar_inputs = {
        "uid": uid,
        "address": address,
        "capacity": 1
    }
    init_solar_data = get_solar_data(init_solar_inputs)
    # if not init_solar_data:
    #     # RETURN ERRANT JSON
    #     return redirect(url_for("views.home", user=current_user))

    # Calculate capacity and mod_quantity
    capacity = suggest_capacity(energy_data, annual_output=init_solar_data.get('output_annual'))
    # noinspection PyTypeChecker
    mod_quantity = suggest_mod_quantity(capacity=capacity, mod_rating=rating)
    state = init_solar_data.get('state')
    state_price = round(import_json('/Users/ryanwright-zinniger/Desktop/SolarCalculator/src/frontend/static/data/SolarCostData.json').get(state), 2)
    if not state_price:
        # Log Error
        pass
    total_price = round(state_price * capacity * 1000)
    tax_credit = round(total_price * 0.3)
    discount_price = round(total_price * 0.7)

    init_data = {
        "uid": uid,
        "name": username,
        "stage": "init",
        "address": address,
        "energy": energy_data,
        "cost": [Decimal(str(n)) for n in cost_data],
        "state": state,
        "state_price": Decimal(str(state_price)),
        "capacity": Decimal(str(capacity)),             # suggested
        "mod_quantity": mod_quantity,                   # suggested
        "tax_credit": tax_credit,
        "total_price": total_price,
        "discount_price": discount_price,
        "status": {
            "status_code": 200,
            "message": "initialization steps completed."
        },
    }

    # Create and run thread to store init inputs
    thread = threading.Thread(target=store_inputs, args=[init_data])
    thread.start()

    return jsonify(init_data)
