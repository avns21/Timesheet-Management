"""Checker functions used to implement validations for the file upload api"""
from sqlalchemy.orm import Session
from src.db.model import models


def get_or_create_id(
    db: Session, model, name_field: str, name_value: str, id_field: str
):
    """Generic function to get or create an ID for a given model"""
    instance = db.query(model).filter(getattr(model, name_field) == name_value).first()

    if instance:
        return getattr(instance, id_field)
    else:
        new_instance = model(**{name_field: name_value})
        db.add(new_instance)
        db.commit()
        db.refresh(new_instance)
        return getattr(new_instance, id_field)


def level_check(row, db: Session):
    """Checks and Assigns level id's to levels
    Else creates a new entry in the database and returns the id corresponding to it"""

    return get_or_create_id(
        db, models.LevelData, "level", row["level"], "level_id")


def team_check(row, db: Session):
    """Checks and Assigns team id's to levels
    Else creates a new entry in the database and returns the id corresponding to it"""

    return get_or_create_id(
        db, models.TeamData, "team", row["team"], "team_id"
    )


def manager_check(row, db: Session):
    """Checks and Assigns manager id's to managers
    Else creates a new entry in the database and returns the id corresponding to it"""

    return get_or_create_id(
        db, models.ManagerData, "manager", row["manager"], "manager_id"
    )


def department_check(row, db: Session):
    """Checks and Assigns department id's to departments
    Else creates a new entry in the database and returns the id corresponding to it"""

    return get_or_create_id(
        db, models.DepartmentData, "department", row["department"], "department_id"
    )


def project_number_check(row, db: Session):
    """Checks and Assigns project number id's to project numbers
    Else creates a new entry in the database and returns the id corresponding to it"""

    return get_or_create_id(
        db,
        models.ProjectNumberData,
        "project_number",
        row["project_number"],
        "project_number_id",
    )


def project_code_check(row, db: Session):
    """Checks and Assigns project code id's to project codes
    Else creates a new entry in the database and returns the id corresponding to it"""
    
    return get_or_create_id(
        db, models.ProjectCodeData, "project_code", row["project_code"], "project_code_id"
    )


def project_name_check(row, db: Session):
    """Checks and Assigns project name id's to project names
    Else creates a new entry in the database and returns the id corresponding to it"""

    return get_or_create_id(
        db, models.ProjectNameData, "project_name", row["project_name"], "project_name_id"
    )


def indxx_id_check(row, db:Session):
    """Checks and Assigns employee_id to indxx_id
    Else creates a new entry in the database and returns the id corresponding to it""" 

    return get_or_create_id(db, models.EmployeeData, "indxx_id",row["indxx_id"],"employee_id")