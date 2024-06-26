import streamlit as st
from plot_dashboard_utils import PlotDashboardUtils
from dashboard_utils import (
    display_get_transactions_file,
    display_get_configuration_file,
    display_home,
    display_data,
    display_sources,
    display_tabs,
    display_date_picker,
)
from data_utils import (
    validate_data,
    add_columns,
    filter_data,
    get_first_last_date,
    get_all_sources,
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

plot_dashboard_utils = PlotDashboardUtils(config)

if file_path is not None:
    org_data = pl.read_excel(file_path)
    validate_data(org_data)
    data = add_columns(org_data)

    first_and_last_date = get_first_last_date(data)

    # Give user option to change date range
    start_date, end_date = display_date_picker(first_and_last_date)

    # Filter data on date range
    data = filter_data(data, start_date, end_date)

    # Display the data in tabular form
    if config["display_data"]:
        display_data(org_data)

    # Get all possible sources within the tiemfeame
    all_sources = get_all_sources(data)

    # Give user option to select a source, timeframe granularity, and category granularity.
    time_frame_col, category_col = display_tabs()
    # Display the net value of every source as a lineplot and as tiles
    plot_dashboard_utils.display_net_value(data, time_frame_col, all_sources)
    # Display the income and outcome for the selected source over time as a lineplot
    # Display the transactions per category over time as a barplot
    sources = display_sources(all_sources)
    income_outcome, transactions_per_category = st.columns(2)
    with income_outcome:
        plot_dashboard_utils.display_income_outcome(
            data, sources, time_frame_col, category_col
        )
    with transactions_per_category:
        plot_dashboard_utils.display_transactions_per_category(
            data, category_col, time_frame_col
        )
    pieplot = plot_dashboard_utils.display_pieplot(data)
    pieplot
else:
    display_home()
    st.stop()
