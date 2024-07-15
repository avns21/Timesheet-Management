"""Renders timesheet data for the user"""

from datetime import date
import json
import pandas as pd
import requests
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from utility.data import timesheet_condition


def timesheet(user_profile):
    """Display the fill timesheet section with editable timesheet grid.
    Args:user_profile -> json of EmployeeData
    Returns: None"""
    msg = timesheet_condition()
    if msg["status"] == "Unfreeze":
        st.title("Timesheet")

        col1, col2 = st.columns(2)
        with col1:
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

        with col2:
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

        if st.button("Generate"):
            response = requests.get(
                "http://127.0.0.1:8000/time_sheet_data",
                params={
                    "indxx_id": user_profile["indxx_id"],
                    "month": month,
                    "year": year,
                },
                timeout=10,
            )

            if response.status_code != 200:
                st.error(response.json().get("detail"))
                if "df_ts" in st.session_state:
                    del st.session_state.df_ts
            else:
                data = response.json()["data"]
                df_ts = pd.DataFrame(data)
                df_ts.columns = ["Day of month", "Work Description", "Status"]
                df_ts["IN"] = "10:00"
                df_ts["OUT"] = "19:00"
                df_ts = df_ts.iloc[:, [0, 3, 4, 1, 2]]

                if df_ts.loc[0]["Day of month"] != 0:
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
                    df_ts = pd.concat([day_0_row, df_ts], ignore_index=True)
                else:
                    df_ts.at[0, "IN"] = ""
                    df_ts.at[0, "OUT"] = ""

                st.session_state.df_ts = df_ts

        if "df_ts" in st.session_state:
            df_ts = st.session_state.df_ts

            gb = GridOptionsBuilder.from_dataframe(df_ts)
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
            grid_height = header_height + buffer_height + (len(df_ts) * row_height)
            gridoptions = gb.build()

            grid_response = AgGrid(
                df_ts,
                gridOptions=gridoptions,
                editable=True,
                fit_columns_on_grid_load=True,
                height=grid_height,
                key="timesheet_grid_ts",
            )

            updated_df_ts = pd.DataFrame(grid_response["data"])
            updated_df_ts.loc[
                updated_df_ts["Status"].isin(
                    ["Saturday", "Sunday", "Holiday", "Leave"]
                ),
                "Work Description",
            ] = ""

            if not df_ts.equals(updated_df_ts):
                st.session_state.df_ts = updated_df_ts

            if st.button("Save", key="save_button"):
                df2_ts = updated_df_ts.copy()

                df2_ts.columns = [
                    "day_of_month",
                    "IN",
                    "OUT",
                    "work_description",
                    "status",
                ]

                df2_ts["indxx_id"] = user_profile["indxx_id"]
                file = df2_ts.to_json(orient="records")
                payload = json.loads(file)

                rr = requests.post(
                    "http://127.0.0.1:8000/add_timesheet", json=payload, timeout=10
                )

                if rr.status_code == 200:
                    st.success("Timesheet saved successfully")

                    st.write("Saved Data:")

                    col_widths = ["20%", "10%", "10%", "45%", "15%"]
                    # background_color = "#f2f2f2"  # Change this to your desired background color
                    background_color = "#000000"

                    styled_df = updated_df_ts.style.set_table_styles(
                        [
                            {
                                "selector": "th.col0",
                                "props": [
                                    ("width", col_widths[0]),
                                    ("background-color", background_color),
                                ],
                            },
                            {
                                "selector": "th.col1",
                                "props": [
                                    ("width", col_widths[1]),
                                    ("background-color", background_color),
                                ],
                            },
                            {
                                "selector": "th.col2",
                                "props": [
                                    ("width", col_widths[2]),
                                    ("background-color", background_color),
                                ],
                            },
                            {
                                "selector": "th.col3",
                                "props": [
                                    ("width", col_widths[3]),
                                    ("background-color", background_color),
                                ],
                            },
                            {
                                "selector": "th.col4",
                                "props": [
                                    ("width", col_widths[4]),
                                    ("background-color", background_color),
                                ],
                            },
                            {
                                "selector": "td",
                                "props": [("background-color", background_color)],
                            },  
                        ]
                    ).set_table_attributes('style="width:100%"')

                    st.write(
                        styled_df.hide(axis="index").to_html(), unsafe_allow_html=True
                    )

    else:
        st.subheader("Timesheet Filling window is over")
