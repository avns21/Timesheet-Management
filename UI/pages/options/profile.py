"""Profile section of the Application"""

import streamlit as st


def show_profile(user_profile):
    """Display the profile section with user profile information."""

    st.markdown(
        """
    <style>
    .profile-container {
        background-color: #F0F2F6 ;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-top: 20px;
    }
    .profile-header {
        font-size: 45px;
        font-weight: bold;
        color: #2C2D2D;
        margin-bottom: 20px;
        text-align: left;
    }
    .profile-details {
        width: 100%;
    }
    .profile-detail {
        font-size: 18px;
        margin-bottom: 10px;
        color: #2C2D2D;
        transition: color 0.3s ease;
    }
    .profile-detail strong {
        color: #000000;
    }
    .profile-detail:hover {
        color: #000000;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<div class='profile-container'>"
        f"<div class='profile-header'>{user_profile['first_name']} {user_profile['last_name']}</div>"
        f"<div class='profile-details'>"
        f"<p class='profile-detail'><strong>Indxx ID:</strong> {user_profile['indxx_id']}</p>"
        f"<p class='profile-detail'><strong>HR Code:</strong> {user_profile['hr_code']}</p>"
        f"<p class='profile-detail'><strong>Department:</strong> {user_profile['department']['department']}</p>"
        f"<p class='profile-detail'><strong>Manager:</strong> {user_profile['manager']['manager']}</p>"
        f"<p class='profile-detail'><strong>Start Date:</strong> {user_profile['start_date']}</p>"
        f"<p class='profile-detail'><strong>Level:</strong> {user_profile['level']['level']}</p>"
        f"<p class='profile-detail'><strong>Project Number:</strong> {user_profile['project_number']['project_number']}</p>"
        f"<p class='profile-detail'><strong>Project Name:</strong> {user_profile['project_name']['project_name']}</p>"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
