"""Download Stoxx Sheet function"""
import base64
import json
from datetime import date
from typing import List

import pandas as pd
import requests
import streamlit as st


def download_stoxx_sheet(options: List[str]):
    """This function takes a list of project code, month and year for which the
    stoxx sheet and summary sheet is to be generated as an input from the user(admin).

    Returns the stoxx sheet and summary sheet of those projects in form of excel sheets
    combined into a zip file, each excel sheet corresponds to a project code."""

    st.header("Download Stoxx Sheet")
    st.subheader("Select the Year and Month:")

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
        month_names = ["January","February","March","April","May","June","July","August",
            "September","October","November","December"]
        valid_months = month_names[:max_val]
        default_index = date.today().month - 1
        month_name = st.selectbox("Month", valid_months, index=default_index)
        month = month_names.index(month_name) + 1  # type: ignore

    st.divider()
    st.subheader("Select the project code:")

    mid_point = len(options) // 2

    left = options[:mid_point]
    right = options[mid_point:]

    data1 = {"options": left, "favorite": [False] * len(left)}
    data2 = {"options": right, "favorite": [False] * len(right)}

    data1_df = pd.DataFrame(data1)
    data2_df = pd.DataFrame(data2)

    select_all = st.checkbox("Select All")

    if select_all:
        data1_df["favorite"] = True
        data2_df["favorite"] = True

    col1, col2 = st.columns(2)

    with col1:
        data1_df = st.data_editor(
            data1_df,
            column_config={
                "favorite": st.column_config.CheckboxColumn(
                    "Select",
                    help="Select project code to download stoxx sheet",
                    default=False,
                )
            },
            disabled=["widgets"],
            hide_index=True,
            key="left",
        )

    with col2:
        data2_df = st.data_editor(
            data2_df,
            column_config={
                "favorite": st.column_config.CheckboxColumn(
                    "Select",
                    help="Select project code to download stoxx sheet",
                    default=False,
                )
            },
            disabled=["widgets"],
            hide_index=True,
            key="right",
        )

    selected_options = (
        data1_df[data1_df["favorite"]]["options"].tolist()
        + data2_df[data2_df["favorite"]]["options"].tolist()
    )

    if st.button("Download Stoxx Sheet"):
        data = {"project_code": selected_options, "month": month, "year": year}
        with st.spinner("Fetching stoxx sheets, Avoid clicking anywhere else... "):
            rr = requests.post(
                "http://127.0.0.1:8000/get_stoxx_sheet/", json=data, timeout=1000
            )
            if rr.status_code == 200:
                b64 = base64.b64encode(rr.content).decode()
                href = f'<a href="data:application/zip;base64,{b64}" download="stoxx_sheets.zip" style = "color: black;">Download Stoxx Sheets</a>'
                st.markdown(href, unsafe_allow_html=True)
                status_list_str = rr.headers.get("X-Status-List")
                status_of_stoxx = json.loads(status_list_str)
                message = ""
                for status in status_of_stoxx:
                    if status["details"] != "Generated successfully":
                        message += status["details"] + "\n"
                    else:
                        message = status["details"] + "\n"
                if status_of_stoxx[0]["details"] != "Generated successfully":
                    st.error(message)
                else:
                    st.error(message)
            else:
                st.error("Failed to generate Stoxx timesheet")
