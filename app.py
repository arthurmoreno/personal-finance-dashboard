import streamlit as st
from utils import (
    get_config,
    get_data,
    get_all_sources,
    get_first_last_date,
    filter_data,
    display_date_picker,
    display_data,
    display_tabs,
    display_sources,
    display_net_value,
    display_income_outcome,
    display_pieplot,
    display_get_file,
    display_transactions_per_category,
)

config = get_config()
st.set_page_config(
    page_title=config["page"]["title"],
    page_icon=config["page"]["icon"],
    layout=config["page"]["layout"],
)

# Let user upload transactions data
file_path = display_get_file()
data = get_data(file_path)

# Get first and last date mentioned in the data
first_and_last_date = get_first_last_date(data)

# Give user option to change date range
start_date, end_date = display_date_picker(first_and_last_date)

# Filter data on date range
data = filter_data(data, start_date, end_date)

# Display the data in tabular form
if config["display_data"]:
    display_data(data)

# Get all possible sources within the tiemfeame
all_sources = get_all_sources(data)

# Give user option to select a source, timeframe granularity, and category granularity.
time_frame_col, category_col = display_tabs()
# Display the net value of every source as a lineplot and as tiles
display_net_value(data, time_frame_col, all_sources)
# Display the income and outcome for the selected source over time as a lineplot
# Display the transactions per category over time as a barplot
sources = display_sources(all_sources)
income_outcome, transactions_per_category = st.columns(2)
with income_outcome:
    display_income_outcome(data, sources, time_frame_col, category_col)
with transactions_per_category:
    display_transactions_per_category(data, category_col, time_frame_col)
pieplot = display_pieplot(data)
pieplot
