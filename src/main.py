# SolarCalculator/src/main.py
# This is the main module for running this program
from src.utils import SAMPLES
from src.backend import inputs as inp, solar_potential as sp, results as res
from logging import basicConfig, getLogger, INFO

basicConfig(
    filename='logs/main.log',
    level=INFO,
    format='%(levelname)s:%(filename)s:%(asctime)s:%(funcName)s(): %(message)s',
    datefmt='%Y/%m/%d-%H.%M.%S',
    filemode='w',
)
LOGGER = getLogger(__name__)


def main():
    LOGGER.info('main() called.')

    # Get Input data
    data_input = inp.input_handler(
        input_type='csv',
        input_source=SAMPLES['csv_valid']
    )

    LOGGER.info(f'InputData successfully received for name: {data_input.name}')
    print('here')
    # Get Solar Potential data
    data_solar_potential = sp.get_solar_potential(
        address=data_input.address,
        annual_consumption=data_input.consumption_annual
    )
    LOGGER.info(f'SolarPotentialData data successfully received for address: {data_solar_potential.address}')

    # Get Results data
    data_results = res.get_results(input_data=data_input, solar_potential_data=data_solar_potential)
    LOGGER.info(f'Results data successfully received for: {data_results.name}')

    return data_input


if __name__ == '__main__':
    main()
