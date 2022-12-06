# ~src/backend/inputs.py
from backend.utils import IntListMonthly, validate_data, FloatListMonthly
from pydantic import BaseModel, PositiveFloat, ValidationError, PositiveInt
from os import PathLike
from typing import Literal, Any


InputTypes = Literal['csv', 'xlsx', 'sheet']


class InputError(Exception):
    """Custom exception for an invalid Input keyword"""
    valid_input_types = ['csv', 'xlsx', 'sheet']


class InputData(BaseModel):
    # Required
    name: str
    address: str
    mod_kwh: PositiveFloat
    consumption_monthly: IntListMonthly
    consumption_annual: PositiveInt
    cost_monthly: FloatListMonthly
    cost_annual: PositiveFloat
    cost_per_kwh: PositiveFloat
    # Optional
    note: str = None
    # Default
    source = "Potential solar data sourced from pvwatts.nrel.gov"
    units_consumption = "kiloWattHours"
    units_cost = "Dollars"
    sym_consumption = "kWh"
    sym_cost = "$"


def _calculate_cost_per_kwh(cost: IntListMonthly, consumption: IntListMonthly) -> PositiveFloat:
    """Calculate the average cost per kWh for inputs and add it to data object (dict)"""
    monthly_cost_per_kwh = [(cos/con) for cos, con in zip(cost, consumption)]
    return round(sum(monthly_cost_per_kwh) / len(monthly_cost_per_kwh), 2)


def _validate_mod_kwh(in_data: str) -> float:
    """Helper function to validate that the data passed is a float."""
    try:
        return float(in_data)
    except ValueError:
        raise ValidationError(
            "The value entered for solar module capacity is invalid."
            + "This must be a decimal between 0 and 1."
        )


@validate_data
def input_csv(file_path: PathLike[str]) -> InputData:
    """Call this function to read a csv with specified format for monthly consumption."""
    from csv import reader

    csv_consumption, csv_cost, csv_user_data = [], [], []
    with open(file_path, 'r') as file:
        csv = reader(file)

        # Get input consumption and cost data from csv
        data_rows = [row for i, row in enumerate(csv) if i in range(1, 13)]
        for row in data_rows:
            csv_consumption.append(round(float(row[2])))
            csv_cost.append(round(float(row[3]), 2))

    with open(file_path, 'r') as file:
        csv = reader(file)
        # Get input user data from csv
        data_rows = [row for i, row in enumerate(csv) if i in range(14, 17)]
        for row in data_rows:
            csv_user_data.append(row[2])

    return InputData(
        name=csv_user_data[0].replace(' ', '').replace('.', ''),
        address=csv_user_data[1],
        mod_kwh=_validate_mod_kwh(in_data=csv_user_data[2]),
        consumption_monthly=csv_consumption,
        consumption_annual=sum(csv_consumption),
        cost_monthly=csv_cost,
        cost_annual=round(sum(csv_cost), 2),
        cost_per_kwh=_calculate_cost_per_kwh(cost=csv_cost, consumption=csv_consumption)
    )


@validate_data
def input_xlsx(file_path: PathLike[str]) -> InputData:
    """Call this function to read a xlsx with specified format for monthly consumption."""
    from openpyxl import load_workbook
    sheet = load_workbook(file_path)['Sheet1']

    xlsx_consumption, xlsx_cost, xlsx_user_data = [], [], []
    for i in range(2, 14):
        xlsx_consumption.append(round(float((sheet[f'C{i}'].value))))
        xlsx_cost.append(round(float(sheet[f'D{i}'].value), 2))

    for i in range(15, 18):
        xlsx_user_data.append(sheet[f'C{i}'].value)

    return InputData(
        name=xlsx_user_data[0].replace(' ', '').replace('.', ''),
        address=xlsx_user_data[1],
        mod_kwh=_validate_mod_kwh(in_data=xlsx_user_data[2]),
        consumption_monthly=xlsx_consumption,
        consumption_annual=sum(xlsx_consumption),
        cost_monthly=xlsx_cost,
        cost_annual=round(sum(xlsx_cost), 2),
        cost_per_kwh=_calculate_cost_per_kwh(cost=xlsx_cost, consumption=xlsx_consumption)
    )


@validate_data
def input_sheets(sheet_id: str) -> InputData:
    """
    Script from below for extracting data from google sheets.
    https://medium.com/analytics-vidhya/how-to-read-and-write-data-to-google-spreadsheet-using-python-ebf54d51a72c

    Will throw error if you haven't run it in a day or two. Need to delete file 'tokens.pickle' from .creds folder then
    rerun and authenticate at the url provided. Should figure out a way around this.
    """
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from os.path import exists as os_exists
    import pickle

    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    sheet_ranges = ['C2:C13', 'D2:D13', 'C15:C17']
    credentials = None
    if os_exists('./.creds/token.pickle'):
        with open('./.creds/token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                r'./.creds/credentials.json', scopes)
            credentials = flow.run_local_server(port=0)
        with open('./.creds/token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    service = build('sheets', 'v4', credentials=credentials)

    # Call the Sheets API
    sheet = service.spreadsheets()
    input_data = sheet.values().batchGet(spreadsheetId=sheet_id, ranges=sheet_ranges).execute()

    user_vals = input_data.get('valueRanges')[2].get('values')
    cons_vals = input_data.get('valueRanges')[0].get('values')
    cost_vals = input_data.get('valueRanges')[1].get('values')

    sheets_consumption = [round(float(sublist[0]), 0) for sublist in cons_vals]
    sheets_cost = [round(float(sublist[0]), 2) for sublist in cost_vals]

    return InputData(
        name=user_vals[0][0].replace(' ', '').replace('.', ''),
        address=user_vals[1][0],
        mod_kwh=_validate_mod_kwh(in_data=user_vals[2][0]),
        consumption_monthly=sheets_consumption,
        consumption_annual=sum(sheets_consumption),
        cost_monthly=sheets_cost,
        cost_annual=round(sum(sheets_cost), 2),
        cost_per_kwh=_calculate_cost_per_kwh(cost=sheets_cost, consumption=sheets_consumption)
    )


def input_handler(input_type: InputTypes, input_source: Any) -> InputData:
    """Handler function for getting the input data based on input type."""

    if input_type not in InputError.valid_input_types:
        raise InputError(
            f"The input '{input_type}' is invalid.\n"
            + f"You must enter one of the following input types: {*InputError.valid_input_types,}"
        )

    if input_type == 'csv':
        return input_csv(file_path=input_source)
    if input_type == 'xlsx':
        return input_xlsx(file_path=input_source)
    if input_type == 'sheet':
        return input_sheets(sheet_id=input_source)


if __name__ == '__main__':
    from main import SAMPLES
    input_handler('csv', SAMPLES['csv'])

