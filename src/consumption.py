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

from .utils import MONTHS_MAP, get_out_obj
from typing import List, AnyStr, Dict


TEMPLATE_DATA_OBJECT = {
    'consumption': [],
    'cost': []
}


def csv_consumption(file_path: AnyStr) -> Dict:
    """Call this function to read a csv with specified format for monthly consumption."""
    from csv import reader

    data = TEMPLATE_DATA_OBJECT
    with open(file_path, 'r') as file:
        csv = reader(file)
        next(csv)
        for row in csv:
            data['consumption'].append(round(float(row[2])))
            data['cost'].append(round(float(row[3])))

    return data


def xlsx_consumption(file_path: AnyStr) -> Dict:
    """Call this function to read a xlsx with specified format for monthly consumption."""
    from openpyxl import load_workbook
    sheet = load_workbook(file_path)['Sheet1']

    data = TEMPLATE_DATA_OBJECT
    for i in range(2, 14):
        data['consumption'].append(round(float((sheet[f'C{i}'].value))))
        data['cost'].append(round(float(sheet[f'D{i}'].value)))

    return data


def sheets_consumption(sheet_id: AnyStr) -> Dict:
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

    data = {
        'consumption': [round(float(sublist[0])) for sublist in cons_vals],
        'cost': [float(sublist[0]) for sublist in cost_vals]
    }

    return data


def manual_input_consumption() -> Dict:
    """Get monthly consumption via python input()"""
    # return [1481, 1317, 1664, 2294, 1938, 1829, 3212, 2641, 2194, 1771, 1678, 1713]

    print("Please enter the monthly consumption and cost values for:")

    data = TEMPLATE_DATA_OBJECT
    for i in range(1, 13):
        data['consumption'].append(round(float(input(f"\tConsumption {MONTHS_MAP[i]}: "))))
        data['cost'].append(round(float(input(f"\tCost {MONTHS_MAP[i]}: ")), 2))

    return data


class Consumption:

    def __init__(self, cons_monthly: List):
        self.cons_monthly = cons_monthly
        self.cons_annual = sum(self.cons_monthly)
        self.cons_obj = get_out_obj(monthly=self.cons_monthly, annual=self.cons_annual)

    def __repr__(self):
        return (
                f"Consumption:\n"
                + f"\tannual consumption = {self.cons_annual}\n"
                + f"\tmonthly consumption = {self.cons_monthly}"
        )


class Cost:

    def __init__(self, cost_monthly: List):
        self.cost_monthly = cost_monthly
        self.cost_annual = sum(self.cost_monthly)
        self.cost_obj = get_out_obj(monthly=self.cost_monthly, annual=self.cost_annual)

    def __repr__(self):
        return (
                f"Cost:\n"
                + f"\tannual cost = {self.cost_annual}\n"
                + f"\tmonthly cost = {self.cost_monthly}"
        )


if __name__ == "__main__":
    print(xlsx_consumption(r'/Users/nicolaaspjedema/Desktop/SolarCalculator/samples/sample_consumption.xlsx'))
