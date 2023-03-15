from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user
import boto3

from datetime import datetime as dt
import json

from ..utils import MONTHS_MAP, DYNAMODB, post_item_to_dynamodb, clean_name, check_http_response

views = Blueprint("views", __name__)

DDB_NAME = "solarCalculatorTable-Inputs"
LAMBDA = boto3.client('lambda')


@views.route("/")
@views.route("/home")
def home():
    """Home view."""

    return render_template("home.html", user=current_user, months=MONTHS_MAP.values())


@views.route("/run-tool", methods=["GET", "POST"])
def run_tool():
    """Run the Solar Calculator tool."""

    # Edge Case - return to create post page if method is not POST
    if request.method != "POST":
        return render_template("home.html", user=current_user)

    # Define request parameters from input form
    time_stamp = dt.now().__str__().replace(' ', '_').replace(':', '.')
    username = clean_name(request.form.get("name"))
    uid = username + time_stamp
    address = request.form.get("address")
    mod_kwh = request.form.get("mod_kwh")
    monthly_data = {
        # Key=month (str): Value=[energyMonth, costMonth] (array[int, float])
    }
    for month in MONTHS_MAP.values():
        monthly_data[month] = [str(request.form.get(f"energy{month}")), str(request.form.get(f"cost{month}"))]

    # Write initial input data to DynamoBD table: solarCalculator-Inputs
    table_item = {
        "uid": username + time_stamp,
        "name": username,
        "address": address,
        "mod_kwh": mod_kwh,
        "monthly_data": monthly_data
    }
    db_response = post_item_to_dynamodb(DYNAMODB.Table(DDB_NAME), item=table_item)
    if not check_http_response(response_code=db_response):
        return redirect(url_for("views.home", user=current_user))

    # Call main function to run the tool
    input_item = {
        "type": "form",
        "form": {
            "uid": uid,
            "name": username,
            "address": address,
            "mod_kwh": 1,
            "monthly_data": {
                "January": [1000, 155.8],
                "February": [1000, 148.8],
                "March": [1000, 144.8],
                "April": [1000, 140.4],
                "May": [1000, 140.2],
                "June": [1000, 134.8],
                "July": [1000, 133.2],
                "August": [1000, 135.8],
                "September": [1000, 134.4],
                "October": [1000, 133.4],
                "November": [1000, 142.8],
                "December": [1000, 148.8]
            }
        }
    }
    lambda_response = LAMBDA.invoke(
        FunctionName='sc-be',
        InvocationType='RequestResponse',
        Payload=json.dumps(input_item)
    )
    if not check_http_response(response_code=lambda_response["StatusCode"]):
        print("An error occurred here!")

    results = json.loads(lambda_response['Payload'].read().decode("utf-8"))
    print(results['status'])

    return render_template("output.html", user=current_user, output=results, months=MONTHS_MAP)
