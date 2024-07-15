"""Login Page"""

import streamlit as st
from app import sidebar
from utility.data import employee_data
import base64


st.set_page_config(
    page_title="TimeSavvy",
)


@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


background_img = get_img_as_base64("theme.png")

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("data:image/png;base64,{background_img}");
background-size: cover;
background-position: center;
background-attachment: fixed;
}}
 
[data-testid="stSidebarContent"] {{
background-color: rgba(34,82,113,0.7);
background-size: cover;
background-position: center;
background-repeat: no-repeat;
background-attachment: fixed;
z-index: 1;
}}
[data-testid="stSidebar"]{{
    height: 885px;
}}
 
 
[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}
 
[data-testid="stToolbar"] {{
right: 2rem;
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)
st.session_state["logged_in"] = st.session_state.get("logged_in", False)


def login_page():
    """Function to render login page"""
    st.markdown(
        """<style>
       .main {
           padding: 2rem;
           border-radius: 10px;
           box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
       }
       .title {
           text-align: center;
           font-family: 'Arial', sans-serif;
            color : white;
           opacity : 1;
       }
       .input {
           width: 100%;
           padding: 0.5rem;
           margin: 0.5rem 0;
           border: 1px solid #ccc;
           border-radius: 5px;
           font-size: 1rem;
       }
       .button {
           background-color: #4e8df5;
           color: white;
           border: none;
           padding: 0.75rem 1.5rem;
           text-align: center;
           text-decoration: none;
           display: inline-block;
           font-size: 1rem;
           margin: 0.5rem 0;
           border-radius: 5px;
           cursor: pointer;
           width: 100%;
       }
       .button:hover {
           background-color: #3a6bb7;
       }
</style>
       """,
        unsafe_allow_html=True,
    )
    st.markdown('<h1 class="title">Timesavvy</h1>', unsafe_allow_html=True)
    indxx_id_input = st.text_input(
        "Enter your Indxx ID:",
        key="indxx_id_input_unique",
        help="Please enter your Indxx ID.",
    )
    indxx_id_input = indxx_id_input.upper()
    if st.button("Login", key="login_button_unique"):
        if indxx_id_input:
            response = employee_data(indxx_id_input)
            if response["indxx_id"] == indxx_id_input:
                st.session_state.logged_in = True
                st.session_state.indxx_id = indxx_id_input
                st.rerun()  # Rerun to ensure the page updates
            else:
                st.error("Please enter a valid Indxx ID")
        else:
            st.error("Please enter the Indxx ID first")


def second_page():
    """Function to render the second page just after login"""
    st.markdown(
        """
<style>
           .logout-button {
               float: right;
               background-color: #4e8df5;
               color: white;
               border: none;
               padding: 0.5rem 1rem;
               text-align: center;
               text-decoration: none;
               display: inline-block;
               font-size: 1rem;
               border-radius: 5px;
               cursor: pointer;
           }
           .logout-button:hover {
               background-color: #3a6bb7;
           }
</style>
       """,
        unsafe_allow_html=True,
    )
    user_profile = employee_data(st.session_state.indxx_id)
    sidebar(user_profile)


# Check if the user is logged in and show the appropriate page
if st.session_state["logged_in"]:
    second_page()
else:
    login_page()
