"""Timesheet Status section of the Admin Panel"""
import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from utility.data import timesheet_condition


def show_df(df: pd.DataFrame):
    df = df.reset_index(drop=True)
    df.index += 1
    df.columns = ["Indxx ID", "Name"]
    row_count = len(df)
    st.write(f"Number of Employees: {row_count}")
    col_widths = ["35%","65%"]
    background_color = "#000000"
                
    styled_df = df.style.set_table_styles(
        [
            {"selector": "th.col0", "props": [("width", col_widths[0]), ("background-color", background_color)]},
            {"selector": "th.col1", "props": [("width", col_widths[1]), ("background-color", background_color)]},
            {"selector": "td", "props": [("background-color", background_color)]},  
        ]
    ).set_table_attributes('style="width:100%"')
                
    st.write(styled_df.hide(axis="index").to_html(), unsafe_allow_html=True)


def timesheet_status(indxx_id, options):
    """Gives the status of timesheets of employees."""
    
    st.markdown(
        """
        <style>
        .window-header {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Timesheet Window"):
        st.markdown(
            '<div class="window-header">Timesheet Window</div>',
            unsafe_allow_html=True,
        )
        fred = ""
        msg = timesheet_condition()
        status_var = 500
        stvar=msg['status']

        col1, col2 = st.columns([1,6])

        with col1:
            freeze_clicked = st.button("Freeze")
        with col2:
            unfreeze_clicked = st.button("Unfreeze")

        st.divider()

        if freeze_clicked:
            fred = {"super_user_id": indxx_id, "freeze": True, "unfreeze": False}
            stvar='Freezed'
            req = requests.post(
            "http://127.0.0.1:8000/update_time_window_status", json=fred, timeout=10
            )
            status_var = req.status_code

        if unfreeze_clicked:
            fred = {"super_user_id": indxx_id, "freeze": False, "unfreeze": True}
            stvar='Unfreezed'
            req = requests.post(
            "http://127.0.0.1:8000/update_time_window_status", json=fred, timeout=10
            )
            status_var = req.status_code

        if status_var == 500:
            st.markdown(
            f"<h5>Current status of timesheet: {stvar}</h5>",
            unsafe_allow_html=True,
        )

        if status_var == 200:
            st.markdown(
            f"<h5>Current status of timesheet: {stvar}</h5>",
            unsafe_allow_html=True,
        )

    with st.expander("Timesheet Status"):
        st.markdown(
            '<div class="window-header">Timesheet Status</div>',
            unsafe_allow_html=True,
        )
        
        
        if st.checkbox("Select all"):
            selected_options = st.multiselect("Select the project code:", options, options)
        else:
            selected_options = st.multiselect("Select the project code:", options)

        if "timesheet_status_data_clicked" not in st.session_state:
            st.session_state["timesheet_status_data_clicked"] = False

        if st.button("Timesheet Status Data"):
            st.session_state["timesheet_status_data_clicked"] = True

        if st.session_state["timesheet_status_data_clicked"]:
            if len(selected_options) == 0:
                st.info("Please select at least one project.")
            else:
                payload = {"project_names_list": selected_options}
                response = requests.post(
                    "http://127.0.0.1:8000/timesheet_status", json=payload, timeout=10
                )

                if response.status_code == 200:
                    data = response.json()

                    df_not_started_employee = pd.DataFrame(data["not_started_data"])
                    df_incomplete_employee = pd.DataFrame(data["incomplete_data"])
                    df_complete_employee = pd.DataFrame(data["complete_data"])

                    labels = ["Completed", "In Progress", "Not Started"]
                    values = [
                        len(df_complete_employee),
                        len(df_incomplete_employee),
                        len(df_not_started_employee),
                    ]

                    total_count = (
                        len(df_complete_employee)
                        + len(df_incomplete_employee)
                        + len(df_not_started_employee)
                    )

                    colors = ['#f03c59','#fb9900','#623eba']

                    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.6, textinfo="label+value",marker = dict(colors=colors))])

                    fig.update_layout(
                        annotations=[
                            dict(
                                text=f"Total: {total_count}",
                                x=0.5,
                                y=0.5,
                                font_size=20,
                                showarrow=False,
                            )
                        ],
                        showlegend=True,
                        plot_bgcolor="rgba(225,225,225,0.7)",
                        # margin=dict(b=0, l=0, r=10),
                        # height=350,
                    )

                    st.plotly_chart(fig)

                    st.markdown(
                        """<style>
                        .main { background-color: #ffffff; }
                        .css-1d391kg { font-family: 'Courier New', Courier, monospace; }
                        </style>""",
                        unsafe_allow_html=True,
                    )

                    st.session_state["not_started_button"] = False
                    st.session_state["in_progress_button"] = False
                    st.session_state["completed_button"] = False

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        not_started_clicked = st.button("Timesheet not started")

                    with col2:
                        inprogress_clicked = st.button("Timesheet in progress")
                    with col3:
                        complete_clicked = st.button("Timesheet completed")

                    if not_started_clicked:
                        st.session_state["not_started_button"] = True
                        st.session_state["timesheet_status_data_clicked"] = True

                    if inprogress_clicked:
                        st.session_state["in_progress_button"] = True
                        st.session_state["timesheet_status_data_clicked"] = True

                    if complete_clicked:
                        st.session_state["completed_button"] = True
                        st.session_state["timesheet_status_data_clicked"] = True

                    if st.session_state["not_started_button"]:
                        st.header("Employees who have not yet started filling timesheet")
                        if not df_not_started_employee.empty:
                            show_df(df_not_started_employee)
                        else:
                            st.info("All employees started filling timesheet")

                    if st.session_state["in_progress_button"]:
                        st.header("Employees with timesheet in progress")
                        if not df_incomplete_employee.empty:
                            show_df(df_incomplete_employee)
                        else:
                            st.info("No employees with timesheet in progress")

                    if st.session_state["completed_button"]:
                        st.header("Employees who have filled timesheet completely")
                        if not df_complete_employee.empty:
                            show_df(df_complete_employee)
                        else:
                            st.info("No employee filled the timesheet completely")
