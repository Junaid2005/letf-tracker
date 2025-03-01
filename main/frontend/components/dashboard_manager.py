"""Component to search up LETF pairs and add/remove them"""

import os
import sys
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
# pylint: disable=wrong-import-position
from models.security_pair import SecurityPair
from frontend.constants import (
    base_column_config,
)
from frontend.helpers.helper import (
    create_df,
    color_change,
)
from db.dashboard import dashboard


def manage_record(action, underlying, letf):
    """Manage a record in your dashboard"""
    if action == "add":
        dashboard.add_record(underlying, letf)
        st.info(f"Added {underlying} and {letf} to your dashboard")
    else:
        dashboard.delete_record(underlying, letf)
        # st.info(f"Removed {underlying} and {letf} to your dashboard")


def dashboard_manager_component():
    """Load the dashboard manager component"""
    with st.container(border=True):
        with st.form("manage_dashboard"):
            input_col_1, input_col_2 = st.columns(2)
            underlying = input_col_1.text_input("Underlying", placeholder="TSLA")
            letf = input_col_2.text_input("LETF", placeholder="3TSL.L")
            submitted = st.form_submit_button("Submit", use_container_width=True)

        # the the whole app refreshes here, this bit below gets removed, it shouldnt.
        if submitted:
            if not underlying or not letf:
                st.error("Please fill in both fields")
                return
            pair = SecurityPair(underlying, letf)
            if pair.is_valid_pair():
                df = create_df([(0, underlying, letf)], False)
                df = df.style.map(color_change, subset=["Ext Hours %"])
                st.dataframe(
                    df,
                    hide_index=True,
                    column_config=base_column_config,
                    use_container_width=True,
                )

                is_present = dashboard.is_pair_present(underlying, letf)
                if is_present:
                    st.button(
                        "Remove from dashboard",
                        use_container_width=True,
                        on_click=lambda: manage_record("remove", underlying, letf),
                    )
                else:
                    st.button(
                        "Add to dashboard",
                        use_container_width=True,
                        on_click=lambda: manage_record("add", underlying, letf),
                    )
            else:
                st.error(
                    """At least one of your tickers is invalid. 
                    Try converting your LETF to a RIC (as done in the placeholder)"""
                )
