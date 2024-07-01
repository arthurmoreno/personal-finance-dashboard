import streamlit as st
from utils.plot_dashboard_utils import PlotDashboardUtils
from utils.dashboard_utils import (
    display_get_transactions_file,
    display_get_configuration_file,
    display_home,
    display_data,
    display_sources,
    display_tabs,
    display_date_picker,
    display_contact_info,
    df_to_excel,
)
from utils.data_utils import (
    validate_data,
    add_columns,
    filter_data,
    get_first_last_date,
    get_all_sources,
)
from utils.constants import (
    default_dashboard_config_path,
    example_categorized_transactions_path,
    exaple_dashboard_config_path,
)
import polars as pl
import yaml
import pandas as pd

if "page_setup" not in st.session_state:
    st.session_state.page_setup = True
    st.set_page_config(
        page_title="Finance Dashboard", page_icon=":bar_chart:", layout="wide"
    )


example_transactions_data = df_to_excel(
    pd.read_excel(example_categorized_transactions_path)
)
with open(
    exaple_dashboard_config_path,
    "r",
) as file:
    yaml_data = file.read()

# Let user upload transactions data
file_path = display_get_transactions_file(example_file=example_transactions_data)
uploaded_config = display_get_configuration_file(example_file=yaml_data)

display_contact_info()

if uploaded_config is not None:
    config = yaml.safe_load(uploaded_config)
else:
    with open(default_dashboard_config_path) as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

plot_dashboard_utils = PlotDashboardUtils(config)

if file_path is not None:
    margins_css = """
    <style>
    @media only screen and (min-width: 768px) {
        .main > div {
            padding-left: 10%;
            padding-right: 10%;
        }
    }
    </style>
    """
    st.markdown(margins_css, unsafe_allow_html=True)

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
    display_home(yaml_data)
    st.stop()
