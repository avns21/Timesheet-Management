"""Comp-Off section of the Application"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta

FASTAPI_URL = "http://127.0.0.1:8000"

def show_table(df:pd.DataFrame):
    
    col_widths = ["5%", "30%", "20%", "25%", "20%"]
    background_color = "#000000"

    styled_df = df.style.set_table_styles(
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

def show_comp_off(user_profile):
    """It takes the from_date, to_date and transaction status as an input.
    For Admin takes the Indxx Id also as an input.
    Avails comp off for the provided data. 
    For Abmin or Super user it displays the data of comp off of the selected month.
    """
    st.title("Comp-Off")

    indxx_id = user_profile["indxx_id"]
    
    if user_profile["role"] is not None:
        col1, col2 = st.columns(2)
        with col1:
            if user_profile["role"]["is_admin"]:
                indxx_id = st.text_input("Indxx ID")
    
        

    days_in_month = (
        datetime(date.today().year, date.today().month % 12 + 1, 1) - timedelta(days=1)
    ).day

    col1, col2 = st.columns(2)

    with col1:
        from_date = st.date_input(
            "From Date",
            value=date.today(),
            min_value=date.today().replace(day=1),
            max_value=date.today().replace(day=days_in_month),
        )

        transaction_status = st.selectbox(
            "Status", options=["NOT AVAILED", "AVAILED"], index=0
        )

    with col2:
        to_date = st.date_input(
            "To Date",
            value=date.today(),
            min_value=date.today().replace(day=1),
            max_value=date.today().replace(day=days_in_month),
        )

    from_date_str = from_date.isoformat()
    to_date_str = to_date.isoformat()

    if st.button("Submit"):
        if indxx_id == '':
            st.error("Please enter Indxx ID")
        else:    
            if from_date_str <= to_date_str:
                rr = requests.post(
                    "http://127.0.0.1:8000/update_comp_off_data",
                    json={
                        "indxx_id": indxx_id,
                        "from_date": from_date_str,
                        "to_date": to_date_str,
                        "transaction_status": transaction_status,
                    },
                    timeout=10,
                )
                response = rr.json()

                if response["detail"] == "Comp Off data added successfully":
                    st.success("Comp Off data added successfully")
                else:
                    st.error(response["detail"])

            else:
                st.error("'From date' should be less than 'To date'")

    if user_profile["role"] is not None:
        st.divider()
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
        endpoint = f"comp_off/{year}/{month}"
        API_URL = f"{FASTAPI_URL}/{endpoint}"
        if st.button("Comp Off Data"):
            response = requests.get(API_URL)
            if response.status_code == 200:
                leavesheets = response.json()
                df = pd.DataFrame(leavesheets)
                if not df.empty : 
                    show_table(df)
                else:
                    st.error("No Comp Off Data for given Month")
                    
            else:
                st.error("Failed to fetch Comp Off data")