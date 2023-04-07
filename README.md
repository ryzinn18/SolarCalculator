# SolarCalculator
A tool for calculating how much you could have saved on energy consumption and cost with solar panels supplementing your energy consumption.

##Design & Stack
The Solar Calculator follows a 3 tier layered architecture. These layers are the Presentation Layer, the Business/Persistence Layer, and the Database layer. Additionally, this project uses a handful of 3rd party Python libraries including Pydantic, Pandas, PyTest, and Flask, and utilizes Amazon Web Services (AWS) tools such as Lambda, EC2, S3, and DynamoDB for it's hosting. This section describes the design and tech stack that comprise this project.

###Presentation Layer
This is the user interface you are using now and includes all of the browser communication logic that make this frontend functional. This layer was developed using the Flask framework for Python. This layer is hosted via an AWS EC2 instance running Ubuntu. This EC2 instance was configured via SSH command line tools as a web server using Nginx, and an application server using Gunicorn. When you enter your information on the home page, this layer takes that information and sends it to the next layer, the Business/Persistence Layer.

###Business/Persistence Layer
This layer is responsible for taking the user’s input and calculating their response. The steps involved in this layer are described in detail in the above Business section. This layer is hosted via AWS Lambda and is called by the Presentation Layer via the AWS SDK. There is also the maintenance component to this layer which contains business logic to remove expired data generated by users. These actions are called chronologically via AWS CloudWatch Events.

All data validation in this step is handled via the Pydantic library; API calls made to 3rd party resources are handled via the Requests library; testing conducted in this layer is facilitated via the PyTest library; graphs generated for the final results are made with MathPlotLib; and structured data manipulation is facilitated with the Pandas library.

###Database Layer
This layer is called by the Business/Persistence layer and is chiefly responsible for storing all of the data necessary for this web application to function. When the Presentation layer is initially invoked by a user’s input, the user’s input data is stored for logging purposes in a DynamoDB table. Next, as results are generated by the Business/Persistence layer, including the graphs and results data, they are written here. Objects like the graphs (.png) and results document (.csv) are stored in S3 buckets while the more raw results data are stored in JSON format in a DynamoDB table.

###Process
The overall process sees data moving down the hierarchy of layers then back up to serve the user with their results. In some cases, the Database layer and Presentation layer skip over the Business/Persistence layer for more direct data storage/serving, making the Business/Persistence layer an Open layer. The two cases it does this is seen when the Presentation layer logs the input data before invoking the Business/Persistence layer. The second case is seen when the application presents the results data; the application's frontend receives the graph objects directly from the database layers, rather than having to buffer the images through the Business/Persistence layer. These design choices were made for the sake of data integrity, in the case of the input data being logged initially, and for efficiency, with respect to the images being served from their S3 buckets directly.

##Business Logic
The Solar Calculator has 3 key modules to its processing which make up its business logic layer: Input Validation, Retrieving Solar Data, and Generating Results. Each module is linked at the beginning of each respective paragraph below.

###Input Validation
This step is handled upon the user submitting their information. Currently, users only have the option to use the form provided on the home page. However, there is prebuilt infrastructure in this module that would allow users to upload .csv or .xslx files, or use a Google Sheet to input and validate their data. At the time this is being written, that capability is being integrated into the frontend and can be expected soon. Upon validating the input data, this module also calculates the average cost per kWh that the user paid.

###Retrieving Solar Data
The address provided by the user is key to retrieving the necessary solar iridescence data. First, the size of the solar array must be computed. To calculate the necessary capacity of the array in kWh we first get a normalized amount of energy produced at the user's location by calling on the National Renewable Energy Laboratory (NREL) API and set our array's capacity to 1. Next, we take the user's annual reported energy consumption and divide it by the normalized solar iridescence - this tells us the size of the array we need in kWh. Finally, we call on the NREL API again using the size of the array as the capacity. This returns the solar potential we could be producing per month.

###Generating Results
This step is the most intensive in terms of calculations and object generation. For this, we pass the validated input data and the solar potential data retrieved in the previous 2 steps to this step’s handler. First, we calculate the monthly production value, potential cost, savings, and cost reduction for the user and store that data in a data frame. Next we generate our graphs using this data.

Once these steps are complete, the necessary data is passed to the frontend and the output is displayed to the user.