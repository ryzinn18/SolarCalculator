"""
ToDo (smaller):
- Create uniform class (pydantic) for data objects.

ToDo (large):
- Unit test all modules.
- Create web UI (JavaScript).
    - Build UI.
    - Build APIs.
- Top down documentation.
- Package!
"""
from src import input_handler
from src.iridescence import get_solar_potential
from src.utils import Metrics

SAMPLE_NAME = 'RyanTest'
SAMPLE_SHEET = '1gneTmzTrGTsJIrjkjzEOYS-Bq7irB_WZ2TJWXMlFp4k'
SAMPLE_ADDRESS = '1417 Bath Street, 93101'

"""SAMPLE_CSV = r'/Users/nicolaaspjedema/Desktop/SolarCalculator/samples/sample_consumption.csv'
SAMPLE_XLSX = r'/Users/nicolaaspjedema/Desktop/SolarCalculator/samples/sample_consumption.xlsx'"""

SAMPLE_CSV = r'/Users/ryanwright-zinniger/Desktop/SolarCalculator/samples/sample_consumption.csv'
SAMPLE_XLSX = r'/Users/ryanwright-zinniger/Desktop/SolarCalculator/samples/sample_consumption.xlsx'

def print_metrics(m) -> None:
    print(
        f"{m.name} - {m.obj_type.title()}\n"
        + f"\tAnnual {m.obj_type.title()} = {m.data_annual} {m.units}\n"
        + f"\tMonthly {m.obj_type.title()} = {m.data_monthly} {m.units}/month"
    )


def main():
    mod_kwh = 0.4   # float(input("What is the production (kWh) for this project's modules?))

    input_object = input_handler.input_csv(file_path=SAMPLE_CSV)
    solar_potential_object = get_solar_potential(address=SAMPLE_ADDRESS, annual_consumption=sum(input_object.get('consumption')))

    metrics_cons = Metrics(
        name=SAMPLE_NAME,
        obj_type='consumption',
        data_monthly=input_object.get('consumption'),
        data_annual=sum(input_object.get('consumption')),
        units='kiloWattHours'
    )
    metrics_cost = Metrics(
        name=SAMPLE_NAME,
        obj_type='cost',
        data_monthly=input_object.get('cost'),
        data_annual=sum(input_object.get('cost')),
        units='dollars'
    )
    metrics_irid = Metrics(
        name=SAMPLE_NAME,
        obj_type='iridescence',
        data_monthly=solar_potential_object.get('iridescence'),
        data_annual=sum(solar_potential_object.get('iridescence')),
        units='kiloWattHours',
        note=solar_potential_object.get('note')
    )

    print_metrics(metrics_cons)
    print_metrics(metrics_cost)
    print_metrics(metrics_irid)


if __name__ == '__main__':
    main()
