# pythonMProject

The goal of this assignment (project) is to write a Python script that automates tasks on Bitbucket, covering both UI testing
using Selenium and API testing using the Bitbucket REST API.

I accomplish its first part - a web-ui client and tests with Selenium.

This solution has a test file - test_bitbucket_activities.py - under src.tests, which contains several tests' scenarious.
The project's source reside under src folder.

The web client, as well as other clients (e.g. base_element.py) resides under src.web.clients folder.
Selenium driver should be created automatically on the first run and will be placed under src.web.drivers folder.

Tests are running under the pytest work frame.
it has a conftest.py file which initiate the client as well as calls for tearDown it the end.

Tests' global (common) args and other are placed under src.cfg.cfg_global at settings.py .
Args per a specific test, resides under src.cfg.cfg_tests, and are named by the test name itself.
"conftest.py" calls these file and load the data, which the tests utilize afterwords.

## About the web client;
it resides under src.we.clients.
All other related code resides under src.web. 
The client uses a wrapper - called "alerts_handling" (which resides in the base_elements.py) and which function as an alerts/popus mitigatgor 
as well it returns True/False upon success/failure -> therefore it is also usable for validation.

## The API uses OAuth 2.0 
You will need both refresh_token and client_secret to instantiate the api client.

## API Client
  - The client resides under src.api.client.
  - All api code placed under src.api.
  - The client has various REST requests which response the requested functionality as described in the assignment.
  - Each function is responsible for a specific action - create, delete, list.
  - Some of them uses data files which resides under src.api.rest_data.
  - These file are read and their content is uses to accomplish the REST calls.

## before running the tests:
  - Create a Python virtual environment and activate it (instruction can be found later in the text below)
  - upgrade the pip package by: **python -m pip install --upgrade pip**
  - install setup.py by: **python setup.py install** (include the dot at the end) - see elaboration below.
  - install the requirements.py by:  **pip install --upgrade -r requirements.txt**

## To run the tests via pytest (for both Windows and Linux)
- First, install the setup.py as mentioned above 
- To run the test via cli, while being in the **project's root tree**, type (and virtualenv is activated):
** python -m ./src pytest --password <bitbucket password> --refresh_token <refresh_token> --client_secret <client_secret> **

## Log files
Are written to the log folder which is under the tree root.
Each test has its own log file, under its name.




