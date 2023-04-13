# SolarCalculator/src/config-template.py

# This is a template file.
# REQUIRED: If you are trying to run this program, you will need to delete '-template' from the module name.
# The nrel_api_key is required for running this program.
# The google_api_sheet_id is only required if you are using google sheets for your inputs.

# REQUIRED: You can attain this at the below location.
# This is for getting the solar potential data from PVWATTS
#     https://developer.nrel.gov/signup/
NREL_API_KEY = '95au0c4ycfTpXzbLTh5yHkaVX6P55qndz3XXUzg6'

# REQUIRED: AWS table name you are using
DYNAMODB_TABLE_NAME = 'solarCalculatorTable'

# OPTIONAL: You need to sign up for a Google sheets API key.
# This is only necessary if you are using a Google sheet for your input data.
# You will also need to run the quickstart.py (see src/archive/quickstart.py) script.
# The below link will walk you through the sign up process.
#     https://handsondataviz.org/google-sheets-api-key.html
GOOGLE_API_SHEET_ID = '1gneTmzTrGTsJIrjkjzEOYS-Bq7irB_WZ2TJWXMlFp4k'
