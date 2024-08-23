import streamlit as st
import pandas as pd
from io import BytesIO
import pandas as pd
from utils.constants import time_frame_mapping, category_col_mapping, colors
import streamlit_shadcn_ui as ui
from streamlit_extras.mention import mention
import yaml


def display_faq():
    with st.expander("**How do I get my transactions?**"):
        st.markdown(
            """
        Some bank offer a download of your transactions in a `CSV` or `Excel` format. For other types of transactions,
        you can manually add them to the file (e.g. cash transactions).
        """
        )

    with st.expander(
        "**What is the description column in the example transaction file?**"
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

        If you are not experienced with excel or python, you can use [this application](https://personalfinancedashboard.streamlit.app/categorize_transactions).
        """,
            unsafe_allow_html=True,
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
        st.stop()


def display_contact_info():
    with st.sidebar:
        st.markdown(
            """
        Get in touch / notify any bugs:
        """
        )
        mention(
            label="Narek Arakelyan",
            icon="https://cdn1.iconfinder.com/data/icons/logotypes/32/circle-linkedin-1024.png",
            url="https://www.linkedin.com/in/n-arakelyan/",
        )
        mention(
            label="Narek Arakelyan",
            icon="github",
            url="https://github.com/NarekAra",
        )
        st.markdown(
            "<br>*This application is hosted on Streamlit Cloud. Terms of service of Streamlit Cloud therefore apply.*",
            unsafe_allow_html=True,
        )


def display_date_picker(first_and_last_date):
    """Displays the date picker and returns the selected dates."""
    dates = ui.date_picker(
        key="date_picker",
        mode="range",
        label="Selected Range",
        default_value=first_and_last_date,
    )
    day_start, day_end = dates
    return day_start, day_end


def display_get_transactions_file(title, example_file=None):
    """Displays the file uploader and returns the uploaded file."""
    uploaded_file = st.file_uploader(title, key=title)
    if example_file:
        st.download_button(
            label="Download example",
            data=example_file,
            file_name="example_transactions_file.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    return uploaded_file


def display_tabs():
    """Displays the tabs for the time frame and category and return their value."""

    def create_tabs(mapping):
        # Key is arbitrary here.
        selected = ui.tabs(
            options=mapping.keys(),
            default_value=list(mapping.keys())[0],
            key=list(mapping.keys())[0],
        )
        selected_col = mapping.get(selected)

        return selected_col

    time_frame_section, category_section, _ = st.columns([3, 3, 6])
    with time_frame_section:
        time_frame_col = create_tabs(time_frame_mapping)
    with category_section:
        category_col = create_tabs(category_col_mapping)
    return time_frame_col, category_col


def display_sources(all_sources):
    sources = st.multiselect(
        label="Sources",
        options=all_sources,
        default=all_sources,
    )
    return sources


def display_data(df):
    """Displays the transaction data."""
    with st.expander("Data Preview"):
        st.dataframe(df)


def display_get_configuration_file(title, example_file=None):
    """Displays the file uploader and returns the uploaded file."""
    uploaded_file = st.file_uploader(title, key=title)
    if example_file:
        # Create a download button
        st.download_button(
            label="Download example",
            data=example_file,
            file_name="example_dashboard_config.yaml",
            mime="application/x-yaml",
        )
    return uploaded_file


def df_to_excel(df):
    # Function to convert DataFrame to Excel
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, index=False, sheet_name="Sheet1")
    writer.close()
    processed_data = output.getvalue()
    return processed_data


MAX_COLS = 4


def get_checkbox_option(option, config, config_name):
    """
    Create 1 checkbox

    Args:
    options (list): Option name.

    Returns:
    Boolean: Value of the checkbox
    """
    # If there is already a value in the config, fetch that
    if (config is not None) & (config_name in config):
        config_settings = config[config_name]
    else:
        config_settings = None

    return st.checkbox(option, value=config_settings)


def get_checkbox_options(options, config, config_name):
    """
    Create a grid of checkboxes for given options.

    Args:
    options (list): List of option names.

    Returns:
    list[bool]: A list of selected options.
    """
    # If there is already a value in the config, fetch that
    if (config is not None) & (config_name in config):
        config_settings = config[config_name]
    else:
        config_settings = None

    # Define number of columns
    n_cols = min(len(options), MAX_COLS)
    selected_options = []

    for i in range(0, len(options), n_cols):
        cols = st.columns(n_cols)
        for col, option in enumerate(options[i : i + n_cols]):
            with cols[col]:
                # Get old default value of checkboxes, if none exist, set to False
                if st.checkbox(
                    option,
                    value=(option in config_settings) if config_settings else False,
                ):
                    selected_options.append(option)

    return selected_options


def get_color_picker_options(options, config, config_name):
    """
    Create a grid of color pickers for given options.

    Args:
    options (list): List of option names.
    label_prefix (str): Prefix for the color picker labels.

    Returns:
    dict: A dictionary mapping option names to their selected colors.
    """
    if (config is not None) & (config_name in config):
        config_settings = config[config_name]
    else:
        config_settings = None
    n_cols = min(len(options), MAX_COLS)
    color_options = {}

    for i in range(0, len(options), n_cols):
        cols = st.columns(n_cols)
        for col, option in enumerate(options[i : i + n_cols]):
            with cols[col]:
                color_option = colors[col % len(colors)]
                color = st.color_picker(
                    label=f"Color for {option}",
                    key=option,
                    value=(
                        config_settings[option]
                        if config_settings is not None and option in config_settings
                        else color_option
                    ),
                )
                color_options[option] = color

    return color_options


def get_number_input_options(options, value, min_value, max_value, config, config_name):
    # Same as get_checkbox_options but for number inputs
    config_settings = config.get(config_name) if config else None
    n_cols = min(len(options), MAX_COLS)
    selected_options = {}

    for i in range(0, len(options), n_cols):
        cols = st.columns(n_cols)
        for col_index, option in enumerate(options[i : i + n_cols]):
            with cols[col_index]:
                input_val = st.number_input(
                    option,
                    value=(
                        config_settings.get(option, value) if config_settings else value
                    ),
                    min_value=min_value,
                    max_value=max_value,
                )
                selected_options[option] = input_val

    return selected_options


def read_config(path):
    # Read config an return its value
    with open(path) as stream:
        try:
            config = yaml.safe_load(stream)
            return config
        except yaml.YAMLError as exc:
            st.error(exc)
