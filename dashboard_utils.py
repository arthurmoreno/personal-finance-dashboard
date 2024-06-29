import streamlit as st
import pandas as pd
from io import BytesIO
import pandas as pd
from constants import (
    time_frame_mapping,
    category_col_mapping,
    sample_transactions_path,
    data_structure_path,
    sample_config_path,
)
import streamlit_shadcn_ui as ui


def display_contact_info():
    with st.sidebar:
        st.markdown(
            """
        ---
        Get in touch:

        LinkedIn → [Narek Arakelyan](https://www.linkedin.com/in/n-arakelyan/)

        GitHub → [Narek Arakelyan](https://github.com/NarekAra)
        """
        )


def display_date_picker(first_and_last_date):
    """Displays the date picker and returns the selected dates."""
    day_start, day_end = ui.date_picker(
        key="date_picker",
        mode="range",
        label="Selected Range",
        default_value=first_and_last_date,
    )
    return day_start, day_end


def display_get_transactions_file():
    """Displays the file uploader and returns the uploaded file."""
    with st.sidebar:
        uploaded_file = st.file_uploader(
            "Upload the transactions.", key="transactions_file"
        )
    return uploaded_file


def display_tabs():
    """Displays the tabs for the time frame, source and category and return their value."""

    def create_tabs(mapping):
        # Key is arbitrary here.
        selected = ui.tabs(
            options=mapping.keys(),
            default_value=list(mapping.keys())[0],
            key=list(mapping.keys())[0],
        )
        selected_col = mapping.get(selected)

        return selected_col

    tabs = st.columns([3, 3, 6])
    with tabs[0]:
        time_frame_col = create_tabs(time_frame_mapping)
    with tabs[1]:
        category_col = create_tabs(category_col_mapping)
    return time_frame_col, category_col


def display_sources(all_sources):
    sources = st.multiselect(
        label="",
        options=all_sources,
        default=all_sources,
    )
    return sources


def display_data(df):
    """Displays the transaction data."""
    with st.expander("Data Preview"):
        st.dataframe(df)


def display_get_configuration_file():
    """Displays the file uploader and returns the uploaded file."""
    with st.sidebar:
        uploaded_file = st.file_uploader("Upload the configuration file.", key="config")
    return uploaded_file


# Function to convert DataFrame to Excel
def df_to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, index=False, sheet_name="Sheet1")
    writer.close()
    processed_data = output.getvalue()
    return processed_data


def display_home():
    example_transactions_data = df_to_excel(pd.read_excel(sample_transactions_path))
    data_structure = pd.read_excel(data_structure_path)
    with open(
        sample_config_path,
        "r",
    ) as file:
        yaml_data = file.read()

    margins_css = """
        <style>
            .main > div {
                padding-left: 10%;
                padding-right: 10%;
            }
        </style>

    """

    st.markdown(margins_css, unsafe_allow_html=True)

    st.markdown(
        """
        <style>
        .main-header {
            font-size: 42px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 0px;
        }
        .sub-header {
            font-size: 24px;
            text-align: center;
            color: #2E9BF5;
        }
        .intro-text {
            font-size: 18px;
            margin-bottom: 5px;
            margin-top: 20px;
        }
        .section-header {
            font-size: 28px;
            font-weight: bold;
            margin-top: 30px;
            margin-bottom: 10px;
        }
        .feature-list, .custom-list {
            font-size: 18px;
        }
        .feature-list li, .custom-list li {
            margin-bottom: 5px;
        }
        .subsection-header {
            font-size: 22px;
            font-weight: bold;
            margin-top: 15px;
            margin-bottom: 15px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="main-header">Personal Finance Dashboard:</div>
        <div class="sub-header">Take Control of Your Finances</div>
        <div class="intro-text">Welcome to a Streamlit-based personal finance dashboard. This intuitive dashboard is designed to give you a visual representation of your finances over time, empowering you to make informed decisions and achieve your financial goals.</div>
        <div class="section-header">What can you see here?</div>
        <ul class="feature-list">
            <li><strong>Track your income and expenses</strong> 📊: See exactly where your money comes from and goes. Easy-to-read visualizations break down your income streams and spending habits, helping you identify areas for potential savings or growth. Gain a comprehensive understanding of your financial patterns to make informed decisions about budgeting and resource allocation.</li>
            <li><strong>Monitor your cash flow</strong> 💸: Stay on top of your incoming and outgoing funds. This dashboard provides clear insight into your current financial liquidity, allowing you to plan for upcoming expenses and avoid potential shortfalls. Anticipate cash crunches and optimize your spending timing to maintain a healthy financial balance.</li>
            <li><strong>View your financial progress</strong> 📈: Charts and graphs track your progress towards your financial goals over time. Whether you're saving for a dream vacation or planning for retirement, this dashboard keeps you motivated and on track. Visualize your long-term financial journey and adjust your strategies based on real-time performance data.</li>
        </ul>
        <div class="section-header">Dashboard Features</div>
        <ul class="feature-list">
            <li><strong>Account Balance Overview:</strong> Current balances with a total sum for quick reference.</li>
            <li><strong>Time Series Analysis:</strong> Balance trends over time for each account.</li>
            <li><strong>Income vs. Expenses:</strong> Weekly, monthly or daily comparison of incoming and outgoing funds, helping you visualize cash flow patterns.</li>
            <li><strong>Expense Categorization:</strong> Breakdown of expenses by category, enabling detailed spending analysis.</li>
            <li><strong>Income Sources:</strong> Distribution of income sources, illustrated in a pie chart.</li>
        </ul>
        <div class="section-header">Customization Options</div>
        <ul class="custom-list">
            <li><strong>Date Range Selection:</strong> Focus on specific time periods using the date picker.</li>
            <li><strong>Data Granularity:</strong> Toggle between Weekly, Daily, and Monthly views for different perspectives.</li>
            <li><strong>Category Filtering:</strong> Select 'Category' or 'Subcategory' to adjust the level of expense detail shown.</li>
            <li><strong>Account Selection:</strong> Use colored toggles to show/hide specific accounts in the visualizations.</li>
        </ul>
        <div class="section-header">Privacy</div>
        <div class="intro-text">This application is hosted on Streamlit Cloud. Terms and services of Streamlit Cloud therefore apply.</div>
        <div class="section-header">Requirements</div>
        <div class="subsection-header">Transactions data</div>
        """,
        unsafe_allow_html=True,
    )
    st.info(
        "You will need to provide an excel file (.xlsx) in the sidebar structured like this:",
        icon="ℹ️",
    )

    # Create a download button
    st.download_button(
        label="Download sample transactions file",
        data=example_transactions_data,
        file_name="sample_transactions_file.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.dataframe(data_structure)
    st.markdown(
        '<div class="subsection-header">Configuration file</div>',
        unsafe_allow_html=True,
    )
    st.info(
        "You can optionally provide a configuration file (.yml) in the sidebar structured like this:",
        icon="ℹ️",
    )

    # Create a download button
    st.download_button(
        label="Download sample configuration file",
        data=yaml_data,
        file_name="sample_dashboard_config.yaml",
        mime="application/x-yaml",
    )

    st.code(yaml_data, language="yml")

    st.markdown(
        '<div class="section-header">Frequently Asked Questions</div>',
        unsafe_allow_html=True,
    )
    with st.expander("**How do I get my transactions?**"):
        st.markdown(
            """
        Some bank offer a download of your transactions in a `CSV` or `Excel` format. For other types of transactions,
        you can manually add them to the file (e.g. cash transactions).
        """
        )

    with st.expander(
        "**What is the description column in the sample transaction file?**"
    ):
        st.markdown(
            """
        This column is not required for the dashboard, however, it is recommend to use this column
        to add all the information about the transaction provided by the bank
        (e.g. description, counterparty account number, name, location etc.).

        It can be used to classify the transactions in categories before providing them to the dashboard.
        """
        )

    with st.expander("**How do I assign categories to transactions?**"):
        st.markdown(
            """
        This is a difficult task. I suggest using excel or python to automatically classify
        the transactions based on the value in the description column.

        E.g. All transactions with the word "McDonalds" in the description can be in the "Food" category and "Fast-food" subcategory.

        After that, you can manually go through the transactions, correct any mistakes and fill in unclassified transactions.
        """
        )

    with st.expander("**What categories should I have?**"):
        st.markdown(
            """
        I suggest having a few special categories:
        * __TRANSFERS__: This is used to cancel out transfers between your accounts.
        * __UNKNOWN__: This is used for transactions that you cannot classify.
        * __STARTING_BALANCE__: This is used to set the starting balance of your accounts if you want to start tracking from a certain date.

        Additionaly, you should specify a category named __INCOME__ for your income, this is required to generate the piepelot.
        You can change the category name in the configuration file.

        Aside from these categories, you can add as many categories or subcategories as you want.
        """
        )
