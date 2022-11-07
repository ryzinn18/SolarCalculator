"""
ToDo (smaller):
- Get results module running
    - Include 'name' attribute in samples and InputData object

ToDo (large):
- Unit test all modules.
- Create web UI (JavaScript).
    - Build UI.
    - Build APIs.
- Top down documentation.
- Package!
"""
from src.input_handler import input_handler
from src.solar_potential import get_solar_potential
from src.results import get_results, Results

SAMPLE_SHEET = '1gneTmzTrGTsJIrjkjzEOYS-Bq7irB_WZ2TJWXMlFp4k'

"""SAMPLE_CSV = r'/Users/nicolaaspjedema/Desktop/SolarCalculator/samples/sample_consumption.csv'
SAMPLE_XLSX = r'/Users/nicolaaspjedema/Desktop/SolarCalculator/samples/sample_consumption.xlsx'"""

SAMPLE_CSV = r'/Users/ryanwright-zinniger/Desktop/SolarCalculator/samples/sample_consumption.csv'
SAMPLE_XLSX = r'/Users/ryanwright-zinniger/Desktop/SolarCalculator/samples/sample_consumption.xlsx'


def main() -> Results:

    data_input = input_handler(
        input_type='csv',
        input_source=SAMPLE_CSV
    )
    data_solar_potential = get_solar_potential(
        address=data_input.address,
        annual_consumption=sum(data_input.consumption_monthly)
    )

    return get_results(input_data=data_input, solar_potential_data=data_solar_potential)


if __name__ == '__main__':
    main()
