"""Login Page"""

import base64
import time

import streamlit as st
from extra_streamlit_components import CookieManager

from app import sidebar
from utility.data import employee_data

st.set_page_config(
    page_title="TimeSavvy",
)

cookie_manager = CookieManager()

@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

sidebar_img = get_img_as_base64("bcg3.jpeg")
background_img = get_img_as_base64("bcg.png")
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
 
 
[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}
 
[data-testid="stToolbar"] {{
right: 2rem;
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

def login_page():
    """Function to render login page"""
    # container = st.container(border=True)
    # with st.container(border=True, height=350):
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
    if st.button("Login", key="login_button_unique"):
        if indxx_id_input:
            response = employee_data(indxx_id_input)
            if response["indxx_id"] == indxx_id_input:
                st.session_state.logged_in = True   
                st.session_state.indxx_id = indxx_id_input
                if "set_page_config" in st.session_state:
                    del st.session_state['set_page_config']
                st.rerun()
            else:
                st.error("Please enter a valid Indxx ID")
        else:
            st.error("Please enter the Indxx ID first")

def second_page(cookie_manager):
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
    sidebar(user_profile,cookie_manager)

if not st.session_state.get("login_state"):
    time.sleep(2) 
# Initialize session state variables if they don't exist
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "indxx_id" not in st.session_state:
    st.session_state.indxx_id = None
if (not cookie_manager.get("indxx_id")) or (cookie_manager.get("indxx_id") == "None"):
    cookie_manager.set("indxx_id", str(st.session_state.indxx_id), key=str(2))
if st.session_state.logged_in:
    cookie_manager.set("logged_in", "true", key=str(1))

# Providing time for collecting cookies
  
# Check if the user is logged in and show the appropriate page
if cookie_manager.get("logged_in") in ["true",True] and cookie_manager.get("indxx_id") not in [
    "None",
    None,
]:
    if not st.session_state.get("indxx_id"):
        st.session_state.indxx_id = cookie_manager.get("indxx_id")
    second_page(cookie_manager)
else:
    login_page()


