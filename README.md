# pythonMProject

The goal of this assignment (project) is to write a Python script that automates tasks on Bitbucket, covering both UI testing
using Selenium and API testing using the Bitbucket REST API.

I accomplish its first part - a web-ui client and tests with Selenium.

This solution has a test file - test_bitbucket_activities.py - under src.tests, which contains several tests' scenarious.
The project's source reside under src folder.

The web client, as well as other clients (e.g. base_element.py) resides under src.web.clients folder.
Selenium driver should be created automatically on the first run and will be placed under src.web.drivers folder.

Tests are running under the pytest workframe.
it has a conftest.py file which initiate the client as well as calls for tearDown it the end.

tests args and other are placed under src.cfg.cfg_global settings.py

## about the main wev client;
it uses a wrapper - called "alerts_handling" (which resides in the base_elements.py) and which function as an alerts/popus mitigatgor 
as well it returns True/False upon success/failure -> therefore it is also usable for validation.

## before running the tests:
  - Create a Python virtual environment and activate it (instruction can be found later in the text below)
  - upgrade the pip package by: **python -m pip install --upgrade pip**
  - install setup.py by: **python -m install .** (include the dot at the end) - see elaboration below.

## To run the tests via pytest (for both Windows and Linux)
- First, install the setup.py as mentions before 
- To run the test via cli, while being in the project's root tree, type (and virtualenv is activated):
  **python -m pytests**
