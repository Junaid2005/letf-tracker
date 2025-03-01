"""Component to view your dashboard"""

import os
import sys
import pandas as pd
from babel.numbers import get_currency_symbol
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
# pylint: disable=wrong-import-position
from models.cache_manager import cache_manager
from frontend.helpers.helper import (
    create_df,
    color_change,
    round_column,
)
from frontend.constants import (
    base_column_config,
)
from core.logger import logger
from db.dashboard import dashboard


def toggle_state(key):
    """Flip the state of any key in the session state"""
    st.session_state[key] = not st.session_state.get(key)


def dashboard_viewer_component():
    """Load the dashboard viewer component"""
    # maybe add a price column for the raw stock
    # see if u can get vertical lines for open and close, somethimg time related on hover too
    records = dashboard.get_all_records()

    if "broker_toggled" not in st.session_state:
        st.session_state["broker_toggled"] = False
        st.session_state["visibility_toggled"] = False

    with st.container(border=True):
        # still dodgy on mobile
        cols = st.columns([0.1,1])

        with cols[0]:
            icon = "link_off" if st.session_state.get("broker_toggled") else "link"
            help_str = (
                "Disconnect from portfolio"
                if st.session_state.get("broker_toggled")
                else "Connect to portfolio"
            )
            st.button(
                label="",
                icon=f":material/{icon}:",
                help=help_str,
                disabled=not bool(os.getenv("TRADING_212_KEY")),
                on_click=lambda: toggle_state("broker_toggled"),
            )

        with cols[1]:
            icon = (
                "visibility_off"
                if st.session_state.get("visibility_toggled")
                else "visibility"
            )
            if not st.session_state.get("broker_toggled"):
                help_str = "Please connect your portfolio to show raw values"
            else:
                help_str = (
                    "Hide raw values"
                    if st.session_state.get("visibility_toggled")
                    else "Show raw values"
                )
            st.button(
                label="",
                icon=f":material/{icon}:",
                help=help_str,
                disabled=not bool(os.getenv("TRADING_212_KEY"))
                or not st.session_state.get("broker_toggled"),
                on_click=lambda: toggle_state("visibility_toggled"),
            )

        if not records:
            st.write("No records to show")
            return

        custom_column_config = base_column_config
        stylable_columns = ["Ext Hours %"]

        if not st.session_state.get("broker_toggled"):
            df = create_df(records, False)

        else:
            cache_manager.refresh_212_cache(records)
            df = create_df(records, True)

            total_ext_hours_returns = (
                df["Ext Hours"].apply(pd.to_numeric, errors="coerce").sum()
            )
            total_row = {
                "Underlying": "",
                "Underlying Change (Intraday)": None,
                "LETF": "",
                "Leverage": "",
                "Ext Hours %": "Total:",
                "Ext Hours": total_ext_hours_returns,
            }

            df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)
            if not st.session_state.get("visibility_toggled"):
                df["Ext Hours"] = df["Ext Hours"].apply(lambda x: "***")

            else:
                account_currency = cache_manager.get_account_currency()
                col_name_ccy = f"Ext Hours {get_currency_symbol(account_currency)}"
                stylable_columns.append("Ext Hours")
                df["Ext Hours"] = df["Ext Hours"].apply(round_column)
                custom_column_config["Ext Hours"] = st.column_config.TextColumn(
                    col_name_ccy
                )

        styled_df = df.style.map(color_change, subset=stylable_columns)

        st.dataframe(
            styled_df,
            hide_index=True,
            column_config=custom_column_config,
        )

        with st.expander("Show Logs"):
            with st.container(height=300):
                # see if there any aesthetic improvements possible here
                raw_logs = logger.get_logs()
                if raw_logs:
                    st.code(raw_logs)
                else:
                    st.text("No logs to show")
