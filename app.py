"""
SNAP CLASS - Online Attendance
==============================

Streamlit entry point.

Routes:
    /                       -> Home (role picker) or dashboard
    /?join-code=CS101       -> Student auto-enroll flow
"""

import streamlit as st

from src.components.dialog_auto_enroll import auto_enroll_dialog
from src.screens.home_screen import home_screen
from src.screens.student_screen import student_screen
from src.screens.teacher_screen import teacher_screen


def _init_session_state() -> None:
    st.session_state.setdefault("login_type", None)
    st.session_state.setdefault("is_logged_in", False)
    st.session_state.setdefault("user_role", None)


def _route() -> None:
    if st.session_state.login_type == "teacher":
        teacher_screen()
    elif st.session_state.login_type == "student":
        student_screen()
    else:
        home_screen()


def _handle_auto_enroll() -> None:
    """If ?join-code=... is present, push the user toward the enroll flow."""
    join_code = st.query_params.get("join-code")
    if isinstance(join_code, list):
        join_code = join_code[0] if join_code else None
    if not join_code:
        return

    # Force the student flow
    if st.session_state.login_type != "student":
        st.session_state.login_type = "student"
        st.rerun()

    # Student is logged in -> show the dialog once
    if (
        "student_data" in st.session_state
        and not st.session_state.get("auto_enroll_shown")
    ):
        st.session_state.auto_enroll_shown = True
        auto_enroll_dialog(join_code)


def main() -> None:
    st.set_page_config(
        page_title="SNAP CLASS - AI Attendance",
        page_icon=":camera:",
        layout="wide",
    )

    _init_session_state()
    _route()
    _handle_auto_enroll()


if __name__ == "__main__":
    main()
