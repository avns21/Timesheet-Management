"""Downloads section"""

from datetime import date
import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder


def show_downloads(user_profile):
    """Display the downloads section where users can download reports and documents."""
    st.title("Download Timesheet")

    col1, col2 = st.columns(2)
    with col2:
        year = st.number_input(
            "Year", min_value=2000, max_value=date.today().year, value=2024, step=1
        )

    max_val = 12

    if date.today().year == year:
        max_val = date.today().month

    with col1:
        month_names = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        valid_months = month_names[:max_val]
        default_index = date.today().month - 1
        month_name = st.selectbox("Month", valid_months, index=default_index)
        month = month_names.index(month_name) + 1  # type: ignore

    if st.button("Fetch Timesheet"):
        response = requests.get(
            "http://127.0.0.1:8000/time_sheet_data",
            params={
                "indxx_id": user_profile["indxx_id"],
                "month": month,
                "year": year,
                "flag": 1,
            },
            timeout=10,
        )
        if response.status_code != 200:
            st.error(response.json().get("detail"))
        else:
            data = response.json()["data"]
            df2_d = pd.DataFrame(data)
            df2_d.columns = ["Day of month", "Work Description", "Status"]
            df2_d["IN"] = "10:00"
            df2_d["OUT"] = "19:00"
            df2_d = df2_d.iloc[:, [0, 3, 4, 1, 2]]
            df2_d.at[0,'IN'] = ''
            df2_d.at[0,'OUT'] = ''
                
            st.session_state.df2_d = df2_d

    if "df2_d" in st.session_state:
        df2_d = st.session_state.df2_d

        gb = GridOptionsBuilder.from_dataframe(df2_d)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_default_column(editable=False)
        # gb.configure_column("Day of month", editable=False)
        # gb.configure_column("IN", editable=False)
        # gb.configure_column("OUT", editable=False)
        # gb.configure_column("Status", editable=False)
        

        
        row_height = 28  
        header_height = 32  
        buffer_height = 30  
        grid_height = header_height + buffer_height + (len(df2_d) * row_height)
        gridOptions = gb.build()

        AgGrid(
            df2_d,
            gridOptions=gridOptions,
            editable=False,
            fit_columns_on_grid_load=True,
            height=grid_height,
            key="timesheet_grid_download",  
        )
        
        csv = df2_d.to_csv(index=False)
        timesheet_filename = (
            f"Timesheet_{user_profile['indxx_id']}_{month_name}_{year}.csv"
        )
        st.download_button(
            label="Download Timesheet as CSV",
            data=csv,
            file_name=timesheet_filename,
            mime="text/csv",
        )
        if "df2_d"  in st.session_state:
            del st.session_state.df2_d
