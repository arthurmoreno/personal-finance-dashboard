import streamlit as st
from utils.plot_dashboard_utils import PlotDashboardUtils
from utils.dashboard_utils import (
    display_data,
    display_sources,
    display_tabs,
    display_date_picker,
    display_faq,
)
from utils.data_utils import (
    validate_data,
    add_columns,
    filter_data,
    get_first_last_date,
    get_all_sources,
)
from utils.constants import paths
import polars as pl
import pandas as pd

_data = None
if st.session_state.cookie_manager.get(cookie="user_logged_in"):
    # If the user is logged in we check if they have a file uploaded
    uid = st.session_state.cookie_manager.get(cookie="user")["localId"]
    if st.session_state.firebase.db.child(uid).child("TransactionsData").get().val():
        st.session_state.cookie_manager.set("file_exists", True, "file_exists")

if st.session_state.cookie_manager.get(cookie="file_exists"):
    # If there is a file (logged in or not), we fetch the latest data
    if st.session_state.cookie_manager.get(cookie="user_logged_in"):
        _data = st.session_state.firebase.read_file(uid, "TransactionsData")
    else:
        _data = st.session_state.df_fetched

if _data is not None:
    # Instansiate the class that will used to generate the plots based some configuration
    plot_dashboard_utils = PlotDashboardUtils(st.session_state.config)

    # Preprocess the data (_data => data)
    _data = pl.from_pandas(_data)
    validate_data(_data)
    data = add_columns(_data)

    first_and_last_date = get_first_last_date(data)

    # Give user option to change date range
    start_date, end_date = display_date_picker(first_and_last_date)

    # Filter data on date range
    data = filter_data(data, start_date, end_date)

    # Display the data in tabular form
    if st.session_state.config["display_data"]:
        display_data(_data)  # display the data the user uploaded

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
    goals = st.session_state.config.get("goals")
    if goals:
        heatmap = plot_dashboard_utils.display_goals_heatmap(data)
        heatmap

    # Plot pieplot of the income -- only if the income category is known.
    if st.session_state.income_category_index is not None:
        pieplot = plot_dashboard_utils.display_pieplot(data)
        if pieplot:
            _, col_center, _ = st.columns(3)
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
        <div class="section-header">Transactions data</div>
        """,
        unsafe_allow_html=True,
    )
    st.warning(
        "👈 Upload an excel (.xlsx) file in the dashboard settings to get started! An example file is provided."
    )
    st.info(
        "The transactions should be structured like this:",
        icon="ℹ️",
    )
    st.dataframe(pd.read_excel(paths["categorized_data_structure"]))
    st.markdown(
        """
        <div class="section-header">FAQ</div>
        """,
        unsafe_allow_html=True,
    )
    display_faq()
