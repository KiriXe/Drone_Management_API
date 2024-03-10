###Drone Management API

This repository contains a Flask-based RESTful API for managing drones and medications. The API provides endpoints for CRUD operations on drones and medications, associations between drones and medications, and additional functionalities. It also includes a scheduled task to check drone battery levels periodically.

###Prerequisites

Make sure you have the following prerequisites installed:

    Python (version 3.6 or higher)
    Pip (Python package installer)

###build
1.To modify the constructor you need to access the setup.py file

2. To create the package use the command

python setup.py sdist

###Manual installation

1.Extract files: 

tar -xvf Drone_Management_API-1.0.tar.gz

2.Navigate to the project directory:

cd Drone_Management_API-1.0

3.Install the required dependencies:

pip install .

###Run the Application in manual installation

Run the following command to start the Flask development server:

python Drone_Management_API.py

The API will be accessible at http://localhost:5000.

###Installation as python package

pip install Drone_Management_API-1.0.tar.gz

###Run the Application as python package

Run the following command to start the Flask development server:

start_Drone

The API will be accessible at http://localhost:5000.

###Configuration

The application is configured to use SQLite as the default database. If you want to use a different database, update the SQLALCHEMY_DATABASE_URI in the app.config section of the app.py file.



###Testing

To run tests, execute the following command:

python testing.py

This will run the test suite and provide feedback on test results.


###Endpoints

The API provides the following endpoints:

    Drones:
        GET /drones: Get all drones.
        GET /drones/<serial_number>: Get details of a specific drone.
        POST /drones: Create a new drone.
        PUT /drones/<serial_number>: Update details of a specific drone.
        DELETE /drones/<serial_number>: Delete a specific drone.

    Medications:
        GET /medications: Get all medications.
        GET /medications/<code>: Get details of a specific medication.
        POST /medications: Create a new medication.
        PUT /medications/<code>: Update details of a specific medication.
        DELETE /medications/<code>: Delete a specific medication.

    Drone-Medication Association:
        POST /drones/with-medications: Load medications onto a drone.

    Drone Service:
        GET /drones/service/loaded-medications/<serial_number>: Get medications loaded on a specific drone.
        GET /drones/service/available-drones: Get the list of available drones.
        GET /drones/service/battery-level/<serial_number>: Get the battery level of a specific drone.

###Scheduled Task

The application includes a scheduled task that runs in the background. This task checks drone battery levels every 300 seconds (5 minutes) and creates an audit log.

###Logging

The application logs events to a file named register.log. This log file uses a rotating file handler to manage log size.