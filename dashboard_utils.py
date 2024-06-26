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
    home_title,
    home_introduction,
    home_privacy,
    home_transactions_info,
    home_config_info,
)
import streamlit_shadcn_ui as ui


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
    st.markdown(
        f"""# {home_title} <span style=color:#2E9BF5><font size=5>Beta</font></span>""",
        unsafe_allow_html=True,
    )
    st.markdown("""\n""")
    st.markdown("#### Greetings")
    st.write(home_introduction)
    st.markdown("#### Privacy")
    st.write(home_privacy)
    st.markdown("#### Requirements")
    st.markdown("###### Transactions data")
    st.info(home_transactions_info, icon="ℹ️")
    example_transactions_data = pd.read_excel(sample_transactions_path)

    # Convert DataFrame to Excel
    example_transactions_data = df_to_excel(example_transactions_data)

    # Create a download button
    st.download_button(
        label="Download sample transactions file",
        data=example_transactions_data,
        file_name="sample_transactions_file.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    df = pd.read_excel(data_structure_path)
    st.dataframe(df)
    st.markdown("###### Configuration file")
    st.info(home_config_info, icon="ℹ️")

    # Streamlit app
    # Read the YAML file
    with open(
        sample_config_path,
        "r",
    ) as file:
        yaml_data = file.read()

    # Create a download button
    st.download_button(
        label="Download sample configuration file",
        data=yaml_data,
        file_name="sample_dashboard_config.yaml",
        mime="application/x-yaml",
    )

    st.code(yaml_data, language="yml")

    st.markdown(
        f"""
        ## Frequently Asked Questions
        """,
        unsafe_allow_html=True,
    )

    with st.expander("**How do I get my transactions?**"):
        st.markdown(
            """
        Some bank offer a download of your transactions in a `CSV` or `Excel` format. For other types of transaction,
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
        -- TRANSFERS: This is used to cancel out transfers between your accounts.
        -- UNKNOWN: This is used for transactions that you cannot classify.
        -- STARTING_BALANCE: This is used to set the starting balance of your accounts if you want to start tracking from a certain date.

        Additionaly, you should specify a category named INCOME for your income, this is required to generate the pipelot.
        You can change the category name in the configuration file.

        Aside from these categories, you can add as many categories or subcategories as you want.
        """
        )
