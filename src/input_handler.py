"""
I have a lot of thoughts about this one. I would like for multiple ways in input the annual consumption:
- upload a .csv or .xlsx
- upload via a google sheet?
- upload via python:
    - probably just using input() initially
    - maybe eventually will have a basic website UI and can input there?

Should probably start with just a simple python class.
- could eventually have a parent class and each of the above options could be child classes?
- could have a handler which decides how to convert the input data from the options above into a uniform class.
"""
from pydantic import BaseModel, conlist, PositiveInt, PositiveFloat
from src.utils import MONTHS_MAP, ListMonthly
from typing import List


class InputData(BaseModel):
    # Mandatory
    # name: str
    consumption: ListMonthly
    cost: ListMonthly
    cost_per_kwh: PositiveFloat
    # Optional
    note: str = None
    # Default
    units_consumption = "kiloWattHours"
    units_cost = "Dollars"
    sym_consumption = "kWh"
    sym_cost = "$"


def _calculate_cost_per_kwh(cost: List, consumption: List) -> PositiveFloat:
    """Calculate the average cost per kWh for inputs and add it to data object (dict)"""
    monthly_cost_per_kwh = [(cos/con) for cos, con in zip(cost, consumption)]
    return round(sum(monthly_cost_per_kwh) / len(monthly_cost_per_kwh), 2)


def input_csv(file_path: str) -> InputData:
    """Call this function to read a csv with specified format for monthly consumption."""
    from csv import reader

    csv_consumption, csv_cost = [], []
    with open(file_path, 'r') as file:
        csv = reader(file)
        next(csv)
        for row in csv:
            csv_consumption.append(round(float(row[2])))
            csv_cost.append(round(float(row[3])))

    return InputData(
        consumption=csv_consumption,
        cost=csv_cost,
        cost_per_kwh=_calculate_cost_per_kwh(cost=csv_cost, consumption=csv_consumption)
    )


def input_xlsx(file_path: str) -> InputData:
    """Call this function to read a xlsx with specified format for monthly consumption."""
    from openpyxl import load_workbook
    sheet = load_workbook(file_path)['Sheet1']

    xlsx_consumption, xlsx_cost = [], []
    for i in range(2, 14):
        xlsx_consumption.append(round(float((sheet[f'C{i}'].value))))
        xlsx_cost.append(round(float(sheet[f'D{i}'].value)))

    return InputData(
        consumption=xlsx_consumption,
        cost=xlsx_cost,
        cost_per_kwh=_calculate_cost_per_kwh(cost=xlsx_cost, consumption=xlsx_consumption)
    )


def input_sheets(sheet_id: str) -> InputData:
    """
    Script from below for extracting data from google sheets.
    https://medium.com/analytics-vidhya/how-to-read-and-write-data-to-google-spreadsheet-using-python-ebf54d51a72c
    """
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from os.path import exists as os_exists
    import pickle

    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    sheet_ranges = ['C2:C13', 'D2:D13']
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

    cons_vals = input_data.get('valueRanges')[0].get('values')
    cost_vals = input_data.get('valueRanges')[1].get('values')


    sheets_consumption = [round(float(sublist[0])) for sublist in cons_vals]
    sheets_cost = [float(sublist[0]) for sublist in cost_vals]

    return InputData(
        consumption=sheets_consumption,
        cost=sheets_cost,
        cost_per_kwh=_calculate_cost_per_kwh(cost=sheets_cost, consumption=sheets_consumption)
    )


def input_manual() -> InputData:
    """Get monthly consumption via python input()"""

    print("Please enter the monthly consumption and cost values for:")

    manual_consumption, manual_cost = [], []

    for i in range(1, 13):
        manual_consumption.append(round(float(input(f"\tConsumption {MONTHS_MAP[i]}: "))))
        manual_cost.append(round(float(input(f"\tCost {MONTHS_MAP[i]}: ")), 2))

    return InputData(
        consumption=manual_consumption,
        cost=manual_cost,
        cost_per_kwh=_calculate_cost_per_kwh(cost=manual_cost, consumption=manual_consumption)
    )


if __name__ == "__main__":
    print(input_xlsx(r'/Users/ryanwright-zinniger/Desktop/SolarCalculator/samples/sample_consumption.xlsx'))
