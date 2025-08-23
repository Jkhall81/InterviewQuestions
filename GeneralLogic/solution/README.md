# GeneralLogic Payroll Calculation

This code calculates payroll based on the specifications laid out in PunchLogicTest.jsonc. The punch_logic.py file will print an array of result objects, and write these results to a results.json.

## Executing This File

1. Setup a virtual environment in Python. There is more than one way to do this, but I usually go with `python -m venv venv`.
2. On windows machines activate the virtual environment by executing .\venv\Scripts\activate while in the same directory as the venv folder.
3. Run pip install -r requirements.txt. This only has stuff in it related to the Pytest tests.
4. Execute the punch_logic.py file with `python punch_logic.py`.
5. To run the tests you need to be right outside of the solution directory and run python -m pytest -v.
