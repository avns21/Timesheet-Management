"""Upload Data section of the Admin Panel"""
import streamlit as st
import requests
import pandas as pd


FASTAPI_URL = "http://127.0.0.1:8000"


def upload_file(file, endpoint):
    try:
        files = {"file": (file.name, file, file.type)}
        response = requests.post(f"{FASTAPI_URL}/{endpoint}", files=files)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        st.error(f"HTTP error occurred: {str(e)}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")



def upload_data_section():
    """Display the file upload section for employee data, leavesheet, and holidaysheet."""
    st.markdown(
        """
        <style>
        .upload-header {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .upload-button {
            margin-top: 10px;
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 10px;
        }
        .upload-button:hover {
            background-color: #45a049;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Employee data file upload
    with st.expander("Upload Employee Data"):
        st.markdown(
            '<div class="upload-header">Upload Employee Data</div>',
            unsafe_allow_html=True,
        )
        employee_file = st.file_uploader(
            "Choose an employee CSV file", type="csv", key="employee"
        )

        if employee_file:
            if st.button("Upload Employee Data", key="employee_button"):
                result = upload_file(employee_file, "add_employee_data")
                if result:
                    st.success(result["message"])

        st.divider()

        st.download_button(
            label="Download Employee Data Sample File",
            data=open(r"pages\options\sample_files\sample_employee_data.csv", "rb"),
            file_name="sample_employee_data.csv",
            mime="text/csv",
        )

    # Leavesheet file upload
    with st.expander("Upload Leavesheet Data"):
        st.markdown(
            '<div class="upload-header">Upload Leavesheet Data</div>',
            unsafe_allow_html=True,
        )
        leavesheet_file = st.file_uploader(
            "Choose a leavesheet CSV file", type="csv", key="leavesheet"
        )

        if leavesheet_file:
            if st.button("Upload Leavesheet", key="leavesheet_button"):
                result = upload_file(leavesheet_file, "upload_leavesheet")
                if result:
                    st.success(result["message"])

        st.divider()

        st.download_button(
            label="Download Leavesheet Sample File",
            data=open(r"pages\options\sample_files\sample_leavesheet_data.csv", "rb"),
            file_name="sample_leavesheet_data.csv",
            mime="text/csv",
        )

    # Holidaysheet file upload
    with st.expander("Upload Holidaysheet Data"):
        st.markdown(
            '<div class="upload-header">Upload Holidaysheet Data</div>',
            unsafe_allow_html=True,
        )
        holidaysheet_file = st.file_uploader(
            "Choose a holidaysheet CSV file", type="csv", key="holidaysheet"
        )

        if holidaysheet_file:
            if st.button("Upload Holidaysheet", key="holidaysheet_button"):
                result = upload_file(holidaysheet_file, "upload_holidaysheet")
                if result:
                    st.success(result["message"])

        st.divider()

        st.download_button(
            label="Download Holiday Sample File",
            data=open(r"pages\options\sample_files\Holiday_Demo_Data.csv", "rb"),
            file_name="sample_holiday_data.csv",
            mime="text/csv",
        )
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("Download Employee Data"):
        st.markdown(
            '<div class="upload-header">Download Employee Data</div>',
            unsafe_allow_html=True,
        )

        endpoint = "employee_data"
        API_URL = f"{FASTAPI_URL}/{endpoint}" 
      
        response = requests.get(API_URL)
        if response.status_code == 200:
            employees = response.json()
            df = pd.DataFrame(employees)
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Employee Data as CSV",
                data=csv,
                file_name='employee_data.csv',
                mime='text/csv',
            )
        else:
            st.error("Failed to fetch employee data")