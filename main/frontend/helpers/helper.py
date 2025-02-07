"""Generic helper file with useful functions"""

import sys
import os
from currency_converter import CurrencyConverter
import pandas as pd
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from models.security_pair import SecurityPair  # pylint: disable=wrong-import-position


@st.cache_data(ttl=60)
def create_df(records, toggle_broker):
    """Return a df after iterating through the records"""
    # should the loadbing bar be external, and progress cached?
    dashboard_loading = st.progress(0, text="Loading Dashboard...")
    total_records = len(records)
    data = []
    if toggle_broker:
        ccy_rates = CurrencyConverter()

    for iteration, db_pair in enumerate(records, start=1):
        dashboard_loading.progress(
            iteration / total_records, f"Comparing {db_pair[1]} and {db_pair[2]}..."
        )
        pair = SecurityPair(db_pair[1], db_pair[2])
        percent_change = pair.get_percent_return()
        row_object = {
            "Underlying": db_pair[1],
            "Underlying Change (Intraday)": pair.underlying_ticker.get_intraday_data(),
            "LETF": db_pair[2],
            "Leverage": pair.letf_ticker.get_leverage(),
            "Ext Hours %": percent_change,
        }
        if toggle_broker:
            row_object["Ext Hours"] = pair.get_absolute_return(
                ccy_rates, percent_change
            )
        data.append(row_object)

    dashboard_loading.empty()

    df = pd.DataFrame(data)
    return df


def color_change(change):
    """Return a color for a given value"""
    if change == "Total:":
        return ""

    if isinstance(change, str):
        try:
            change = float(change.rstrip("%"))
        except ValueError:
            return "color: red"
    # add theming for the green
    color = "lime" if change >= 0 else "red"
    return f"color: {color}"


def round_column(value):
    """Round a value to 2dp"""
    if isinstance(value, (int, float)):
        return f"{value:.2f}"
    return value
