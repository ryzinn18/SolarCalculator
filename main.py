"""
main module for testing SolarCalculator
"""
from src import consumption
from src.iridescence import get_iridescence as irid
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

    consumption_object = consumption.csv_consumption(file_path=SAMPLE_CSV)
    iridescence_object = irid(address=SAMPLE_ADDRESS, annual_consumption=sum(consumption_object.get('consumption')))

    metrics_cons = Metrics(
        name=SAMPLE_NAME,
        obj_type='consumption',
        data_monthly=consumption_object.get('consumption'),
        data_annual=sum(consumption_object.get('consumption')),
        units='kiloWattHours'
    )
    metrics_cost = Metrics(
        name=SAMPLE_NAME,
        obj_type='cost',
        data_monthly=consumption_object.get('cost'),
        data_annual=sum(consumption_object.get('cost')),
        units='dollars'
    )
    metrics_irid = Metrics(
        name=SAMPLE_NAME,
        obj_type='iridescence',
        data_monthly=iridescence_object.get('iridescence'),
        data_annual=sum(iridescence_object.get('iridescence')),
        units='kiloWattHours',
        note=iridescence_object.get('note')
    )

    print_metrics(metrics_cons)
    print_metrics(metrics_cost)
    print_metrics(metrics_irid)


if __name__ == '__main__':
    main()
