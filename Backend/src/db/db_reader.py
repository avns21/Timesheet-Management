"""Functions that fetches and reads the data stored in the database"""

from datetime import date
from typing import Dict, List

import pandas as pd
from sqlalchemy import and_, desc, extract, select
from sqlalchemy.orm import Session

from src.db.model import models
from src.db.schema import schemas


def get_project_name_ids(db: Session, project_name_list: List[str]) -> List[int]:
    """Retrieve a list of project_name_id for each project_name in the project_names list.
    Args:project_names (list[str]): List of project names.
    Returns: list[int]: List of corresponding project_name_id.
    """
    result = (
        db.query(models.ProjectNameData.project_name_id)
        .filter(models.ProjectNameData.project_name.in_(project_name_list))
        .all()
    )
    project_name_ids = [row[0] for row in result]
    return project_name_ids


def get_inprogress_timesheet_employee_data(db: Session, names_id_list: List[int]):
    """Gives us the Employees that have not filled the timesheet completely."""
    
    current_month = date.today().month
    current_year = date.today().year

    incomplete_timesheet_employee_data = (
        db.query(
            models.EmployeeData.indxx_id,
            models.EmployeeData.first_name,
            models.EmployeeData.last_name,
        )
        .outerjoin(
            models.TimeSheetData,
            and_(
                models.TimeSheetData.month == current_month,
                models.TimeSheetData.year == current_year,
                models.EmployeeData.employee_id == models.TimeSheetData.employee_id
                
            ),
        )
        .filter(
            and_(
                models.EmployeeData.project_name_id.in_(names_id_list),
                models.TimeSheetData.work_description == "",
                models.TimeSheetData.status == "",
            )
        )
        .distinct()
    )

    results = incomplete_timesheet_employee_data.all()
    df = pd.DataFrame(results)
    if df is not None and not df.empty:
        df["name"] = df["first_name"] + " " + df["last_name"]
        df.drop(columns=["first_name", "last_name"], inplace=True)
    return df


def get_not_started_timesheet_employee_data(db: Session, names_id_list: List[int]):
    """Gives us the Employees that have not filled the timesheet completely."""
    
    current_month = date.today().month
    current_year = date.today().year

    not_started_timesheet_employee_data = (
        db.query(
            models.EmployeeData.indxx_id,
            models.EmployeeData.first_name,
            models.EmployeeData.last_name,
        )
        .outerjoin(
            models.TimeSheetData,
            and_(
                models.EmployeeData.employee_id == models.TimeSheetData.employee_id,
                models.TimeSheetData.month == current_month,
                models.TimeSheetData.year == current_year
            ),
        )
        .filter(
            and_(
            models.EmployeeData.project_name_id.in_(names_id_list),
                models.TimeSheetData.work_description == None
            )
        )
    )

    results = not_started_timesheet_employee_data.all()
    df = pd.DataFrame(results)
    if df is not None and not df.empty:
        df["name"] = df["first_name"] + " " + df["last_name"]
        df.drop(columns=["first_name", "last_name"], inplace=True)
    return df


def get_completed_timesheet_employee_data(
    db: Session,
    df_incomplete_employee: pd.DataFrame,
    df_not_started_employee: pd.DataFrame,
    names_id_list: List[int],):
    """Gives us the Employees that have filled the timesheet completely."""

    employee = (
        db.query(
            models.EmployeeData.indxx_id,
            models.EmployeeData.first_name,
            models.EmployeeData.last_name,
        )
        .filter(models.EmployeeData.project_name_id.in_(names_id_list))
        .all()
    )

    df_employee = pd.DataFrame(employee)
    if df_employee is not None and not df_employee.empty:
        df_employee["name"] = df_employee["first_name"] + " " + df_employee["last_name"]
        df_employee.drop(columns=["first_name", "last_name"], inplace=True)

    combined_subset = pd.concat([df_incomplete_employee, df_not_started_employee])
    if not combined_subset.empty:
        result_df = (
            df_employee.merge(combined_subset, how="outer", indicator=True)
            .query('_merge == "left_only"')
            .drop("_merge", axis=1)
        )
        return result_df
    else:
        return df_employee


def get_user_info(db: Session, indxx_id: str):
    """Takes indxx_id as an input. 
    Returns Employees information using Indxx ID"""
    
    return (
        db.query(models.EmployeeData)
        .filter(models.EmployeeData.indxx_id == indxx_id)
        .first())


def get_timesheet_by_indxx_id_and_date(
    db: Session, indxx_id: str, month: int, year: int
) -> List[Dict[str, str]]:
    """ Retrieves and combines timesheet data for a specified employee, month, and year if present into database.
    Else returns empty list.
    Args:indxx_id (str): The index ID of the employee.
        month and year (int): The month and year for which to retrieve data.
    Returns:
        List[Dict[str, str]]: A list of dictionaries containing combined timesheet and leave data,sorted by day_of_month.
    """

    employee = db.query(models.EmployeeData).filter_by(indxx_id=indxx_id).first()
    if not employee:
        return []
    employee_id = employee.employee_id

    timesheet_entries = (
        db.query(models.TimeSheetData)
        .filter_by(employee_id=employee_id, month=month, year=year)
        .all()
    )
    if not timesheet_entries:
        return []

    combined_dict = {}

    for entry in timesheet_entries:
        combined_dict[entry.day_of_month] = {
            "day_of_month": entry.day_of_month,
            "work_description": entry.work_description,
            "status": entry.status,
        }

    combined_list = sorted(combined_dict.values(), key=lambda x: x["day_of_month"])
    return combined_list


def get_project_codes(db: Session) -> list[str]:
    """gets the list of all unique project codes from the project_code_data table."""
    
    project_codes = db.query(models.ProjectCodeData.project_code).all()
    return [code[0] for code in project_codes]


def get_project_names(db: Session) -> list[str]:
    """gets the list of all unique project names from the project_name_data table."""
    
    project_names = db.query(models.ProjectNameData.project_name).all()
    return [code[0] for code in project_names]


def get_time_stamp(db:Session):
    """Gets the most recent window status"""

    return db.query(models.TimeWindowData).filter_by().order_by(desc(models.TimeWindowData.time_stamp)).first()


def convert_to_schema(employee):
   """Converts the data of employee to schemas.EmployeeDataSchema format."""

   return schemas.EmployeeDataSchema(
       indxx_id=employee.indxx_id,
       hr_code=employee.hr_code,
       first_name=employee.first_name,
       last_name=employee.last_name,
       start_date=employee.start_date,    
       level=employee.level.level if employee.level else None,
       team=employee.team.team if employee.team else None,
       department=employee.department.department if employee.department else None,
       manager=employee.manager.manager if employee.manager else None,
       project_number=employee.project_number.project_number if employee.project_number else None,
       project_code=employee.project_code.project_code if employee.project_code else None,
       project_name=employee.project_name.project_name if employee.project_name else None
   )


def fetch_compoff_data(year: int, month: int, db: Session):
   """
   Fetch Comp Off data for a specific month and year.
   Args:
       year (int): The year for which to fetch leave sheet data.
       month (int): The month for which to fetch leave sheet data.
       db (Session): The database session.
   Returns:
       List[schemas.LeaveSheetData]: A list of Comp Off data schemas.
   """
   stmt = select(
       models.LeaveSheetData.leavesheet_id,
       (models.EmployeeData.first_name + " " + models.EmployeeData.last_name).label('employee_name'),
       models.LeaveSheetData.leave_status,
       models.LeaveSheetData.leave_date,
       models.LeaveSheetData.transaction_status
   ).join(models.EmployeeData).where(
       models.LeaveSheetData.leave_status == "Comp Off",
       extract('year', models.LeaveSheetData.leave_date) == year,
       extract('month', models.LeaveSheetData.leave_date) == month
   )
   result = db.execute(stmt).all()
   return [
       schemas.LeaveSheetData(
           employee_name=row[1],
           leave_status=row[2],
           leave_date=row[3],
           transaction_status=row[4],
       )
       for row in result
   ]
