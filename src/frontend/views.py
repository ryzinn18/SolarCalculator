from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user

from datetime import datetime as dt
from decimal import Decimal

from .validate_inputs import *
from .invoke_lambda import *
from .invoke_ddb import *
from src.utils.utils import MONTHS_MAP, clean_name, import_json, get_item_from_dynamodb, update_item_in_dynamodb

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

    # Create time stamp for sort key
    time_stamp = dt.now().__str__().replace(' ', '_').replace(':', '.')
    # Define input request parameters
    username = clean_name(request.args.get("username"))
    address = request.args.get("address")
    rating = request.args.get("rating")
    energy_monthly = request.args.get("energy").split(",")
    cost_monthly = request.args.get("cost").split(",")
    # Validate inputs
    if not validate_init_data(username, address, rating, energy_monthly, cost_monthly):
        # RETURN ERRANT JSON
        return redirect(url_for("views.home", user=current_user))
    # Transform to correct data types
    rating = round(float(rating), 2)
    energy_monthly = [int(n) for n in energy_monthly]
    cost_monthly = [float(n) for n in cost_monthly]
    # Calculate annual figures
    energy_annual = sum(energy_monthly)
    cost_annual = round(sum(cost_monthly))

    # Create init data item
    init_data = {
        "username": username,
        "time_stamp": time_stamp,
        "address": address,
        "rating": Decimal(str(rating)),
        "energy_monthly": energy_monthly,
        "cost_monthly": [Decimal(str(n)) for n in cost_monthly],
        "energy_annual": energy_annual,
        "cost_annual": cost_annual,
        "state_residence": None,
        "state_price": None,
        "output_monthly": None,
        "output_annual": None,
        "array_capacity": None,
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
    address = request.args.get('address')
    capacity = float(request.args.get('capacity'))

    # Call Lambda sc-be-solar for init solar data
    solar_inputs = {
        "address": address,
        "capacity": capacity
    }
    init_solar_data = invoke_lambda(function='sc-be-solar', inputs=solar_inputs)
    if not init_solar_data:
        return jsonify({"status": {"status_code": 442, "message": "Unable to retrieve Solar data."}})

    solar_data = {
        "address": address,
        "capacity": capacity,
        "output_monthly": init_solar_data.get('output_monthly'),
        "output_annual": init_solar_data.get('output_annual'),
        "state": init_solar_data.get('state'),
        "status": {
            "status_code": 200,
            "message": "Solar data retrieved successfully."
        }
    }

    return jsonify(solar_data)


@views.route('/inputs/finalize/')
def finalize():
    """Get and calculate final figures for getting results and update the db with it."""
    print(f"args: {request.args}")

    username = clean_name(request.args.get("username"))
    time_stamp = request.args.get('time')
    capacity = round(float(request.args.get('capacity')), 2)
    rating = round(float(request.args.get('rating')), 2)
    state = request.args.get('state')
    output_monthly = [round(int(n)) for n in request.args.get('monthly').split(",")]
    output_annual = round(float(request.args.get('annual')))

    state_price = round(float(import_json(
        '/Users/ryanwright-zinniger/Desktop/SolarCalculator/src/frontend/static/data/SolarCostData.json').get(state)),
                        2)
    if not state_price:
        return jsonify({"status": {"status_code": 400, "message": "Failed to load state cost data."}})

    mod_quantity = int(capacity // rating) + 1
    total_price = round(state_price * capacity * 1000)
    tax_credit = round(total_price * 0.3)
    discount_price = round(total_price * 0.7)

    # Declare update parameters
    ddb_update_expression = "set state_residence=:sr, state_price=:sp, output_monthly=:om, output_annual=:oa, " \
                            "array_capacity=:ac, mod_quantity=:mq, total_price=:tp, tax_credit=:tc, discount_price=:dp"
    ddb_update_values = {
        ':sr': state,
        ':sp': Decimal(str(state_price)),
        ':om': output_monthly,
        ':oa': output_annual,
        ':ac': Decimal(str(capacity)),
        ':mq': mod_quantity,
        ':tp': total_price,
        ':tc': tax_credit,
        ':dp': discount_price
    }
    response = update_item_in_dynamodb(
        ddb_name='sc-inputs',
        key={'username': username, 'time_stamp': time_stamp},
        update_expression=ddb_update_expression,
        values=ddb_update_values
    )
    if not check_http_response(response_code=response):
        return jsonify({"status": {"status_code": 400, "message": "Failed to upload DDB."}})
    else:
        return jsonify({"status": {"status_code": 200, "message": "Data finalized."}})


@views.route('/results/')
def get_results():
    """"""

    # Declare parameters for getting item from ddb
    name = request.args.get('username')
    username = clean_name(request.args.get('username'))
    time_stamp = request.args.get('time')

    # Get item from ddb
    response = get_item_from_dynamodb(ddb_name='sc-inputs', key={'username': username, 'time_stamp': time_stamp})
    if not check_http_response(response_code=response.get('ResponseMetadata').get('HTTPStatusCode')):
        return jsonify({"status": {"status_code": 400, "message": "Failed to upload DDB."}})

    # Declare data item from response for easy access
    data = response.get('Item')

    # Call Lambda sc-be-results for results data
    inputs = {
        "name": name,
        "username": username,
        "time_stamp": time_stamp,
        "address": data.get('address'),
        "state": data.get('state_residence'),
        "price_per_watt": round(float(data.get('state_price')), 2),
        "rating": round(float(data.get('rating')), 2),
        "capacity": round(float(data.get('array_capacity')), 2),
        "mod_quantity": int(data.get('mod_quantity')),
        "cost_monthly": [round(float(n), 2) for n in data.get('cost_monthly')],
        "cost_annual": int(data.get('cost_annual')),
        "energy_monthly": [int(n) for n in data.get('energy_monthly')],
        "energy_annual": int(data.get('energy_annual')),
        "output_monthly": [int(n) for n in data.get('output_monthly')],
        "output_annual": int(data.get('output_annual')),
        "total_price": int(data.get('total_price')),
        "tax_credit": int(data.get('tax_credit')),
        "discount_price": int(data.get('discount_price')),
    }
    results_data = invoke_lambda(function='sc-be-results', inputs=inputs)
    if not results_data:
        return jsonify({"status": {"status_code": 442, "message": "Unable to retrieve Solar data."}})

    return jsonify({"status": {"status_code": 200, "message": "Data finalized."}})