"""Central streamlit app file"""

import os
import sys
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from db.dashboard import DashboardDB
from core.logger import logger
from frontend.components.dashboard_manager import dashboard_manager_component
from frontend.components.dashboard_viewer import dashboard_viewer_component

logger.set_debug()

dashboard = DashboardDB()

st.set_page_config(page_title="LETF Tracker")
st.title("LETF Tracker")

if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = "Dashboard"

tab = st.radio(
    "Select Tab",
    ["Dashboard", "Search Pair"],
    horizontal=True,
    label_visibility="collapsed",
)

st.session_state.selected_tab = tab

if tab == "Dashboard":
    dashboard_viewer_component()
elif tab == "Search Pair":
    dashboard_manager_component()
