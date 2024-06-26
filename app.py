import streamlit as st
from data_utils import FinanceDashboard
from dashboard_utils import (
    display_get_transactions_file,
    display_get_configuration_file,
    display_home,
)
import polars as pl
import yaml

if "page_setup" not in st.session_state:
    st.session_state.page_setup = True
    st.set_page_config(
        page_title="Finance Dashboard", page_icon=":bar_chart:", layout="wide"
    )

# Let user upload transactions data
file_path = display_get_transactions_file()
uploaded_config = display_get_configuration_file()

if uploaded_config is not None:
    config = yaml.safe_load(uploaded_config)
else:
    with open("sample_resources/default_dashboard_config.yml") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

finance_dashboard = FinanceDashboard(config)

if file_path is not None:
    org_data = pl.read_excel(file_path)
    data = finance_dashboard.add_columns(org_data)

    first_and_last_date = finance_dashboard.get_first_last_date(data)

    # Give user option to change date range
    start_date, end_date = finance_dashboard.display_date_picker(first_and_last_date)

    # Filter data on date range
    data = finance_dashboard.filter_data(data, start_date, end_date)

    # Display the data in tabular form
    if config["display_data"]:
        finance_dashboard.display_data(org_data)

    # Get all possible sources within the tiemfeame
    all_sources = finance_dashboard.get_all_sources(data)

    # Give user option to select a source, timeframe granularity, and category granularity.
    time_frame_col, category_col = finance_dashboard.display_tabs()
    # Display the net value of every source as a lineplot and as tiles
    finance_dashboard.display_net_value(data, time_frame_col, all_sources)
    # Display the income and outcome for the selected source over time as a lineplot
    # Display the transactions per category over time as a barplot
    sources = finance_dashboard.display_sources(all_sources)
    income_outcome, transactions_per_category = st.columns(2)
    with income_outcome:
        finance_dashboard.display_income_outcome(
            data, sources, time_frame_col, category_col
        )
    with transactions_per_category:
        finance_dashboard.display_transactions_per_category(
            data, category_col, time_frame_col
        )
    pieplot = finance_dashboard.display_pieplot(data)
    pieplot
else:
    display_home()
    st.stop()
