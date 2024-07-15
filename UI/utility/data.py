from typing import List
import requests
from datetime import datetime


def employee_data(indxx_id: str):
    """Returns data of an employee from  employee_data table.
    Args: indxx_id (str): The Indxx ID of the employee.
    Return: All the details of the employee in json format."""
    
    response = requests.get(f"http://127.0.0.1:8000/users/{indxx_id}", timeout=10)

    if response.status_code == 200:
        profile = response.json()
        return profile
    else:
        return {"indxx_id": "NA"}


def timesheet_condition():
    response = requests.get(
        "http://127.0.0.1:8000/get_time_window_status",
        timeout=10,
    )
    if response.status_code == 200:
        react = response.json()
        return react
    else:
        return {"status": "Freeze"}


def project_code_list() -> List[str]:
    """Returns a list of all the project codes in the database."""

    response = requests.get("http://127.0.0.1:8000/project_codes")

    if response.status_code == 200:
        options = response.json()
        return options
    else:
        return []


def project_name_list() -> List[str]:
    """Returns a list of all the project codes in the database."""

    response = requests.get("http://127.0.0.1:8000/project_names")

    if response.status_code == 200:
        options = response.json()
        return options
    else:
        return []
