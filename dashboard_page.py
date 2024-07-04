import streamlit as st
from utils.plot_dashboard_utils import PlotDashboardUtils
from utils.dashboard_utils import (
    display_get_transactions_file,
    display_get_configuration_file,
    display_data,
    display_sources,
    display_tabs,
    display_date_picker,
    display_contact_info,
    df_to_excel,
    display_faq,
)
from utils.data_utils import (
    validate_data,
    add_columns,
    filter_data,
    get_first_last_date,
    get_all_sources,
    validate_config_format,
)
from utils.constants import (
    default_dashboard_config_path,
    example_categorized_transactions_path,
    exaple_dashboard_config_path,
    categorized_data_structure_path,
)
import polars as pl
import yaml
import pandas as pd

data_structure = pd.read_excel(categorized_data_structure_path)
example_transactions_data = df_to_excel(
    pd.read_excel(example_categorized_transactions_path)
)
with open(
    exaple_dashboard_config_path,
    "r",
) as file:
    yaml_data = file.read()

# Let user upload transactions data
file_path = display_get_transactions_file(
    title="categorized transactions (.xlsx)", example_file=example_transactions_data
)
uploaded_config = display_get_configuration_file(
    title="dashboard configuration (.yml)", example_file=yaml_data
)

display_contact_info()

if uploaded_config is not None:
    config = yaml.safe_load(uploaded_config)
    result = validate_config_format(config)

    if "errors" in result:
        for error in result["errors"]:
            st.error(error["loc"][0] + " " + error["msg"])
            st.stop()
else:
    with open(default_dashboard_config_path) as stream:
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

    # Only plot the heatmap of the goals if goals are provided.
    if config["goals"] != {}:
        heatmap = plot_dashboard_utils.display_goals_heatmap(data)
        heatmap

    # Plot pieplot of the income
    _, col_center, _ = st.columns(3)
    pieplot = plot_dashboard_utils.display_pieplot(data)
    with col_center:
        pieplot
else:
    st.markdown(
        """
        <div class="main-header">Personal Finance Dashboard</div>
        <div class="sub-header">Take Control of Your Finances</div>
        <div class="intro-text">Welcome to a Streamlit-based personal finance dashboard. This intuitive dashboard is designed to give you a visual representation of your finances over time, empowering you to make informed decisions and achieve your financial goals.</div>
        <div class="section-header">What can you see here?</div>
        <ul class="feature-list">
            <li><strong>Track your income and expenses</strong> 📊: See exactly where your money comes from and goes. Easy-to-read visualizations break down your income streams and spending habits, helping you identify areas for potential savings or growth. Gain a comprehensive understanding of your financial patterns to make informed decisions about budgeting and resource allocation.</li>
            <li><strong>Monitor your cash flow</strong> 💸: Stay on top of your incoming and outgoing funds. This dashboard provides clear insight into your current financial liquidity, allowing you to plan for upcoming expenses and avoid potential shortfalls. Anticipate cash crunches and optimize your spending timing to maintain a healthy financial balance.</li>
            <li><strong>View your financial progress</strong> 📈: Charts and graphs track your progress towards your financial goals over time. Whether you're saving for a dream vacation or planning for retirement, this dashboard keeps you motivated and on track. Visualize your long-term financial journey and adjust your strategies based on real-time performance data.</li>
        </ul>
        <div class="section-header">Requirements</div>
        <div class="subsection-header">Transactions data</div>
        """,
        unsafe_allow_html=True,
    )
    st.warning(
        '👈 Upload an excel (.xlsx) file in the sidebar or click *"Download example"* to get started!'
    )
    st.info(
        "The transactions should be structured like this:",
        icon="ℹ️",
    )
    st.dataframe(data_structure)
    st.markdown(
        '<div class="subsection-header">Configuration file</div>',
        unsafe_allow_html=True,
    )
    st.warning(
        '👈 Optionally upload a configuration file (.yml) in the sidebar or click *"Download example"* to get started!'
    )
    st.info(
        "The configuration file should be structured like this:",
        icon="ℹ️",
    )
    st.code(yaml_data, language="yml")

    st.markdown(
        '<div class="section-header">Frequently Asked Questions</div>',
        unsafe_allow_html=True,
    )

    display_faq()
