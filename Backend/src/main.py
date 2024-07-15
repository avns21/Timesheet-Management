"""API to upload a file"""
import json
import logging
from datetime import date, datetime
from typing import List

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session

from src.db import db_reader as read
from src.db import db_writer as write
from src.db.model import models
from src.db.model.database import engine, get_db
from src.db.schema import schemas
from src.service import BytesIO, create_timesheet_template, generate_stoxx_timesheet

logging.basicConfig(
    level=logging.INFO, filemode="a", format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
MESSAGE = {"message": "File uploaded successfully and data stored in database."}


@app.get("/", tags=["Swagger UI"])
async def docs_redirect():
    """Redirect to docs - Swagger UI."""
    
    logger.info("Redirecting to docs")
    return RedirectResponse(url="/docs")


@app.post("/add_employee_data", tags=["Employee Data"])
async def add_employee_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Takes the csv file of employee data as input and updates it into employee_data table of the database."""
    
    try:
        write.save_employee_data_to_db(file, db)
        return MESSAGE
    except Exception as e:
        logger.error("Failed to upload employee data file: %s", e)
        raise HTTPException(status_code=406, detail="Failed to upload file.") from e


@app.post("/upload_leavesheet", tags=["Leavesheet"])
async def upload_leavesheet(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Takes the csv file of leaves data as input and updates it into leavesheet_data table of the database."""

    try:
        write.save_leavesheet_data_to_db(file, db)
        return MESSAGE
    except Exception as e:
        logger.error("Failed to upload leavesheet file: %s", e)
        raise HTTPException(status_code=406, detail="Failed to upload leave sheet file.") from e


@app.get("/users/{indxx_id}", response_model=schemas.EmployeeData, tags=["Employee Data"])
async def get_user(indxx_id: str, db: Session = Depends(get_db)):
    """Gets the information of the Employee using their Indxx ID
    Returns the json of the Employee data in the schemas.EmployeeData format."""

    try:
        db_user = read.get_user_info(db, indxx_id=indxx_id)
        return db_user
    except Exception as e:
        logger.error("Failed to fetch user data for Indxx id %s:%s", indxx_id, e)
        raise HTTPException(detail=str(e), status_code=500) from e


@app.get("/time_sheet_data", tags=["Timesheet"])
async def time_sheet_data(indxx_id: str, month: int, year: int, db: Session = Depends(get_db), flag: int = 0):
    """Gets the Timesheet data of an Employee using their Indxx Ids.
    If the timesheet data for a specified month of an employee is not present in the database,
    then it creates the timesheet template with data of leaves, holidays, comp_off(written as leave), 
    weekends in the status column and returns it. 
    Args: indxx_id , month , year
    Return: timesheet data in json format.
    """
    try:
        timesheet_data = read.get_timesheet_by_indxx_id_and_date(
            db, indxx_id=indxx_id, month=month, year=year
        )
        if not timesheet_data:
            if ((flag == 0)
                and (month == date.today().month)
                and (year == date.today().year)):

                timesheet_template = create_timesheet_template(indxx_id, month, year, db)

                return {"data": timesheet_template, "error": None}
            
            raise ValueError("Timesheet data for the user for the specified month/year doesn't exist.")
        
        return {"data": timesheet_data, "error": None}

    except Exception as e:
        logger.error("Failed to fetch timesheet data for Indxx ID %s: %s{e}", indxx_id, e)
        raise HTTPException(detail=str(e), status_code=500) from e
    

@app.post("/add_timesheet", tags=["Timesheet"]) 
async def add_timesheet(timesheet_data: List[schemas.TimeSheetData], db: Session = Depends(get_db)):
    """Takes the JSON(List[schemas.TimeSheetData]) as an input and updates the data into database."""

    try:
        write.save_timesheetdata_to_db_streamlit(timesheet_data, db)
        return MESSAGE
    except Exception as e:
        logger.error("Failed to upload timesheet data: %s", e)
        raise HTTPException(
            status_code=406, detail="Failed to upload timesheet file."
        ) from e


@app.post("/update_comp_off_data", tags=["Leavesheet"])      
async def update_comp_off_data(data: schemas.CompOffData, db: Session = Depends(get_db)):
    """Updates data of Comp Off in leavesheet_data table"""
    
    try:
        write.create_comp_off_df(db, indxx_id = data.indxx_id, from_date = data.from_date, 
                                    to_date = data.to_date, transaction_status = data.transaction_status)
        return {"detail": "Comp Off data added successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{str(e)}")


@app.post("/timesheet_status", tags=["Timesheet"])
async def timesheet_status(names_list: schemas.SelectedOptions, db: Session = Depends(get_db)):  #: List[str]
    """Gives the status(completed, inprogress and not yet started) of timesheet of Employees.
    Takes the list of the project names, data of employees corresponding to the list is then returned."""
    
    try:
        names_id_list = read.get_project_name_ids(db, names_list.project_names_list)
        df_not_started_employee = read.get_not_started_timesheet_employee_data(db, names_id_list)
        df_incomplete_employee = read.get_inprogress_timesheet_employee_data(db, names_id_list)
        df_complete_employee = read.get_completed_timesheet_employee_data(db,df_incomplete_employee
                                                                            ,df_not_started_employee, names_id_list)

        return {"incomplete_data": df_incomplete_employee,"not_started_data":df_not_started_employee
                , "complete_data": df_complete_employee}

    except:
        raise HTTPException(status_code=500,detail="No employees found who has not submitted the timesheets for this month.",)


@app.post("/upload_holidaysheet", tags=["Holiday Sheet"])
async def upload_holidaysheet(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Takes the csv file of holiday data as input and updates it into holiday_data table of the database."""

    try:
        write.save_holiday_data_to_db(file, db)
        return MESSAGE
    except Exception as e:
        logger.error("Failed to upload holiday data")
        raise HTTPException(detail=str(e), status_code=500) from e


@app.post("/create_role", tags=["Role Allocation"])
async def create_role(user: schemas.RoleCreate, db: Session = Depends(get_db)):
    """API for creating and updating roles of a specific user. 
    Args: Indxx ID (schemas.RoleCreate)"""

    try:
        return write.create_user_role(db=db, user=user)
    except Exception as e:
        logger.error("Failed to create role")
        raise HTTPException(detail=str(e), status_code=500) from e


@app.get("/project_codes", response_model=List[str], tags=["General Data"])
async def get_project_codes(db: Session = Depends(get_db)):
    """API for fetching list of unique project codes and returning it."""
    
    try:
        return read.get_project_codes(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch project codes") from e


@app.get("/project_names", response_model=List[str], tags=["General Data"])
async def get_project_names(db: Session = Depends(get_db)):
    """API for fetching list of unique project names and returning it."""
    
    try:
        return read.get_project_names(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch project names") from e
    

@app.post("/get_stoxx_sheet", tags=["Stoxx Sheet"])     
async def get_stoxx_sheet(project_code_data: schemas.StoxxSheet, db: Session = Depends(get_db)):
    """API that takes list of project codes, month & year as an input and generates a zip file of stoxx sheet and summary sheet of the project codes in the list."""
    
    try:
        zip_buffer, status_list = generate_stoxx_timesheet(project_code_data, db)
        headers = {
            "Content-Disposition": "attachment; filename=stoxx_sheets.zip",
            "X-Status-List":json.dumps(status_list)
            }
        return StreamingResponse(
            BytesIO(zip_buffer),
            media_type="application/x-zip-compressed",
            headers=headers,
        )
    except Exception as e:
        logger.error("Failed to generate stoxx timesheet")
        raise HTTPException(detail=str(e), status_code=500) from e
    
    
@app.post("/update_time_window_status", tags=["Timesheet Window"])      
async def update_time_window_status(time_window_data:schemas.TimeWindow,db:Session = Depends(get_db)):
    """API to freeze/unfreeze user-timesheet window and add that data into the time_window_data table."""
    
    try:
        write.insert_update_in_timewindow(time_window_data,db)
        return {'message':'Status of timesheet window updated'}
    except Exception as e:
        logger.error("Failed create time window")
        raise HTTPException(detail=str(e), status_code=500) from e


@app.get("/get_time_window_status", tags=["Timesheet Window"])    
async def get_time_window_status(db:Session = Depends(get_db)):
    """API to get the status(freeze or unfreeze) of user-timesheet window.
    Returns a json ({'status':'[status]'})"""

    try:
        time_sheet_status=read.get_time_stamp(db)
        if time_sheet_status:
            if time_sheet_status.time_stamp.month != datetime.now().month:
                return{'status':'Unfreeze'}
            else:
                return {'status':time_sheet_status.status}
        else:
            return {'status':'Unfreeze'}
    except Exception as e:
        logger.error("Failed to get time window")
        raise HTTPException(detail=str(e), status_code=500) from e


@app.get("/employee_data", tags=["Employee Data"])     
async def get_all_employee_data(db: Session = Depends(get_db)):    
    """ Fetch all employee data from the database.
    Returns: List[EmployeeDataSchema]: A list of employee data schemas."""

    try:
        employees = db.query(models.EmployeeData).all()
        return [read.convert_to_schema(employee) for employee in employees]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/comp_off/{year}/{month}", response_model=List[schemas.LeaveSheetData], tags=["Leavesheet"]) 
async def get_comp_off_data(year: int, month: int, db: Session = Depends(get_db)):
   """ Fetch Comp Off data for a specific month and year.
   Args: year and month for which to fetch comp off data.
   Returns: List[LeaveSheetData]: A list of Comp Off data."""

   try:
       return read.fetch_compoff_data(year, month, db)
   except Exception as e:
       raise HTTPException(status_code=500, detail=str(e))