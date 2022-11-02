"""
main module for testing SolarCalculator
"""

import src.consumption as Cons
import src.iridescence as Irid
from src.utils import Metrics, Data

SAMPLE_NAME = 'RyanTest'
SAMPLE_CSV = r'/Users/nicolaaspjedema/Desktop/SolarCalculator/samples/sample_consumption.xlsx'
SAMPLE_XLSX = r'/Users/nicolaaspjedema/Desktop/SolarCalculator/samples/sample_consumption.xlsx'
SAMPLE_SHEET = '1gneTmzTrGTsJIrjkjzEOYS-Bq7irB_WZ2TJWXMlFp4k'
SAMPLE_ADDRESS = '1417 Bath Street, 93101'


def print_metrics(m) -> None:
    print(
        f"{m.name} - {m.obj_type.title()}\n"
        + f"\tAnnual {m.obj_type.title()} = {m.data_annual} {m.units}\n"
        + f"\tMonthly {m.obj_type.title()} = {m.data_monthly} {m.units}/month"
    )


def main():
    cons = Cons.sheets_consumption(sheet_id=SAMPLE_SHEET)
    annual_cons = sum(cons.get('consumption'))
    annual_cost = sum(cons.get('cost'))
    #print(cons.get('consumption'))
    irid = Irid.Iridescence(
        address=SAMPLE_ADDRESS,
        annual_consumption=annual_cons
    )

    metrics_cons = Metrics(
        name=SAMPLE_NAME,
        obj_type='consumption',
        data_monthly=cons.get('consumption'),
        data_annual=annual_cons,
        units='kiloWattHours'
    )
    metrics_cost = Metrics(
        name=SAMPLE_NAME,
        obj_type='cost',
        data_monthly=cons.get('cost'),
        data_annual=annual_cost,
        units='dollars'
    )
    metrics_irid = Metrics(
        name=SAMPLE_NAME,
        obj_type='iridescence',
        data_monthly=irid.irid_monthly,
        data_annual=irid.irid_annual,
        units='kiloWattHours'
    )

    data_cons = Data(metrics=metrics_cons)
    data_cost = Data(metrics=metrics_cost)
    data_irid = Data(metrics=metrics_irid)

    print_metrics(data_cons)
    print_metrics(data_cost)
    print_metrics(data_irid)


if __name__ == '__main__':
    main()
