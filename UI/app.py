"""This includes access and framework to all the pages."""

import streamlit as st

# from extra_streamlit_components import CookieManager
from streamlit_option_menu import option_menu

from pages.options.comp_off import show_comp_off
from pages.options.dashboard import show_dashboard
from pages.options.downloads import show_downloads
from pages.options.profile import show_profile
from pages.options.timesheet import timesheet

# cookie_manager = CookieManager()


def sidebar(user_profile):
    """Rendering sidebar"""
    # st.session_state.login_state = True
    with st.sidebar:
        if isinstance(user_profile, dict):

            st.markdown(
                f"""<div style="text-align: center; z-index: 0; position: relative;">
                <img src="https://th.bing.com/th/id/OIP.y4vDl1sXQFbum_5f_WHvtgHaFR?rs=1&pid=ImgDetMain"
                style="border-radius: 50%; width: 96px; height: 80px;">
                <h2>{user_profile['first_name']} {user_profile['last_name']}</h2>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if user_profile["role"] is not None:
                if (
                    user_profile["role"]["is_super_user"]
                    or user_profile["role"]["is_admin"]
                ):
                    section = option_menu(
                        menu_title=None,
                        options=[
                            "Admin Panel",
                            "Profile",
                            "Timesheet",
                            "Downloads",
                            "Comp Off",
                            "Logout",
                        ],
                        icons=[
                            "grid",
                            "person",
                            "calendar",
                            "download",
                            "file-earmark-text",
                            "box-arrow-right",
                        ],
                        menu_icon="cast",
                        default_index=0,
                    )
                else:
                    section = option_menu(
                        menu_title=None,
                        options=[
                            "Profile",
                            "Timesheet",
                            "Downloads",
                            "Comp Off",
                            "Logout",
                        ],
                        icons=[
                            "person",
                            "calendar",
                            "download",
                            "file-earmark-text",
                            "box-arrow-right",
                        ],
                        menu_icon="cast",
                        default_index=0,
                    )
            else:
                section = option_menu(
                    menu_title=None,
                    options=[
                        "Profile",
                        "Timesheet",
                        "Downloads",
                        "Comp Off",
                        "Logout",
                    ],
                    icons=[
                        "person",
                        "calendar",
                        "download",
                        "file-earmark-text",
                        "box-arrow-right",
                    ],
                    menu_icon="cast",
                    default_index=0,
                )
    if not st.session_state.get("prev_selected"):
        st.session_state["prev_selected"]=section
    if st.session_state.get("prev_selected")!=section:
        st.session_state["prev_selected"]=section
        for i in ["df_ts","df_ft"]:
            if i in st.session_state:
                del st.session_state[i]


    if section == "Admin Panel":
        show_dashboard(user_profile)

    elif section == "Profile":
        show_profile(user_profile)

    elif section == "Timesheet":
        # if "df_ts"  in st.session_state:
        #     del st.session_state.df_ts
        timesheet(user_profile)

    elif section == "Downloads":
        show_downloads(user_profile)

    elif section == "Comp Off":
        show_comp_off(user_profile)

    elif section == "Logout":
        st.session_state.logged_in = False
        st.session_state.indxx_id = None

        # cookie_manager.set("indxx_id", str(st.session_state.indxx_id), key=str(2))
        # cookie_manager.set("logged_in", "false", key=str(1))
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
