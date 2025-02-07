"""Constants file relating to the ui"""

import streamlit as st

base_column_config = {
    "Underlying Change (Intraday)": st.column_config.LineChartColumn(
        "Change (Intraday)"
    )
}
