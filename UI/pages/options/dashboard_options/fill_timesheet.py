"""Function of 'Edit Timesheet' section of the Admin Panel"""
import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder
from datetime import date
import json


def fill_timesheet():
    """Function of 'Edit Timesheet' section of the Admin Panel.
    Uses the same API as the Timesheet section of the sidebar. 
    Takes Indxx ID, month and year as an Input."""
    
    st.title("Timesheet")

    col1, col2, col3 = st.columns(3)
    with col1:
        indxx_id = st.text_input("Indxx ID:")

    with col2:
        year = st.number_input(
            "Year",
            min_value=2000,
            max_value=date.today().year,
            value=date.today().year,
            step=1,
        )

    max_val = 12

    if date.today().year == year:
        max_val = date.today().month

    with col3:
        month_names = [
            "January","February","March","April","May","June","July","August","September",
            "October","November","December",]
        valid_months = month_names[:max_val]
        default_index = date.today().month - 1
        month_name = st.selectbox("Month", valid_months, index=default_index)
        month = month_names.index(month_name) + 1  # type: ignore

    if st.button("Generate"):
        if indxx_id == '':
            st.error("Please enter an Indxx ID")
        else:
            response = requests.get(
                "http://127.0.0.1:8000/time_sheet_data",
                params={"indxx_id": indxx_id, "month": month, "year": year},
                timeout=10,
            )

            if response.status_code != 200:
                st.error(response.json().get("detail"))
                if "df_ft" in st.session_state:
                    del st.session_state["df_ft"]
            else:
                data = response.json()["data"]
                df_ft = pd.DataFrame(data)
                df_ft.columns = ["Day of month", "Work Description", "Status"]
                df_ft["IN"] = "10:00"
                df_ft["OUT"] = "19:00"
                df_ft = df_ft.iloc[:, [0, 3, 4, 1, 2]]

                if df_ft.loc[0]["Day of month"] != 0:
                    day_0_row = pd.DataFrame(
                        [
                            {
                                "Day of month": 0,
                                "IN": "",
                                "OUT": "",
                                "Work Description": "",
                                "Status": "",
                            }
                        ]
                    )
                    df_ft = pd.concat([day_0_row, df_ft], ignore_index=True)
                else:
                    df_ft.at[0,'IN'] = ''
                    df_ft.at[0,'OUT'] = ''
                
                st.session_state["df_ft"] = df_ft


    if "df_ft" in st.session_state:
        df_ft = st.session_state["df_ft"]

        gb = GridOptionsBuilder.from_dataframe(df_ft)
        gb.configure_pagination(paginationAutoPageSize=True)
        
        if(month != date.today().month or year != date.today().year):
            gb.configure_default_column(editable=False)
        else :
            gb.configure_default_column(editable=True)
            gb.configure_column("Day of month", editable=False)
            gb.configure_column("IN", editable=False)
            gb.configure_column("OUT", editable=False)
            gb.configure_column("Status", editable=False)

        row_height = 28
        header_height = 32
        buffer_height = 50
        grid_height = header_height + buffer_height + (len(df_ft) * row_height)
        gridoptions = gb.build()

        # Display the grid
        grid_response = AgGrid(
            df_ft,
            gridOptions=gridoptions,
            editable=True,
            fit_columns_on_grid_load=True,
            height=grid_height,
            key="timesheet_grid_ft",
        )

        # Get the edited data back
        updated_df_ft = pd.DataFrame(grid_response["data"])
        updated_df_ft.loc[
            updated_df_ft["Status"].isin(["Saturday", "Sunday", "Holiday", "Leave"]),
            "Work Description",
        ] = ""

        if not df_ft.equals(updated_df_ft):
            st.session_state.df_ft = updated_df_ft

        if st.button("Save", key="save_button"):
            df2_ft = updated_df_ft.copy()

            df2_ft.columns = [
                "day_of_month",
                "IN",
                "OUT",
                "work_description",
                "status",
            ]

            df2_ft["indxx_id"] = indxx_id
            file = df2_ft.to_json(orient="records")
            payload = json.loads(file)

            rr = requests.post(
                "http://127.0.0.1:8000/add_timesheet", json=payload, timeout=10
            )

            if rr.status_code == 200:
                st.success("Timesheet saved successfully")

                st.write("Saved Data:")

                col_widths = ["20%", "10%", "10%", "45%", "15%"]
                background_color = "#000000"  # Change this to your desired background color
                
                styled_df = updated_df_ft.style.set_table_styles(
                    [
                        {"selector": "th.col0", "props": [("width", col_widths[0]), ("background-color", background_color)]},
                        {"selector": "th.col1", "props": [("width", col_widths[1]), ("background-color", background_color)]},
                        {"selector": "th.col2", "props": [("width", col_widths[2]), ("background-color", background_color)]},
                        {"selector": "th.col3", "props": [("width", col_widths[3]), ("background-color", background_color)]},
                        {"selector": "th.col4", "props": [("width", col_widths[4]), ("background-color", background_color)]},
                        {"selector": "td", "props": [("background-color", background_color)]},  # Apply background color to table cells
                    ]
                ).set_table_attributes('style="width:100%"')
                
                st.write(styled_df.hide(axis="index").to_html(), unsafe_allow_html=True)