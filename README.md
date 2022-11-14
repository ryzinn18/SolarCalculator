# SolarCalculator
A tool for calculating how much you could have saved on energy prices in the past year with solar panels supplementing your energy consumption.

## Current Capabilities
Can accept inputs via csv, xlsx, or Google sheets documents.
  Uses csv library, openpyxl library and Google developer API to access the respective data.
Calls the PVWatts (DOE) API for potential energy production for the past year specific to user's address.
  Uses requests library to call the PVWatts API.
Compares user's consumption and cost over the past year by visualizing the data in a easy to read graph.
  Uses matplotlib to visualize the data.
All iput data validated using pydantic basemodel classes.
All functionality tested via pytest.

## Future capabilites
Working to add a web UI and API to communicate with backend.
Have a simple web UI users can enter their inputs in manually or upload one of the accepted file types (csv, xlsx, google sheets).
Display outputs to the user and allow them to download the necessary info.
