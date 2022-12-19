# SolarCalculator
A tool for calculating how much you could have saved on energy prices in the past year with solar panels supplementing your energy consumption.

## Current Capabilities
Can accept inputs via csv, xlsx, or Google sheets documents.
Uses csv library, openpyxl library and Google developer API to access the respective data.
Calls the PVWatts (U.S. DOE) API via the requests library for potential energy production over the past year specific to user's address.
Compares user's consumption and cost over the past year by visualizing the data via matplotlib in a easy to read graphs.
All input data validated using pydantic BaseModel classes.
All functionality tested via pytest.
Conventional logging capabilities added to aid with debugging when necessary.

## Future capabilities
Will soon add AWS DynamoDB and S3 buckets for storing output data and output objects (graphs) respectively by user.
Working to add a web UI and API to communicate with backend.
Have a simple web UI users can enter their inputs in manually or upload one of the accepted file types (csv, xlsx, google sheets).
Display outputs to the user and allow them to download the necessary info.
