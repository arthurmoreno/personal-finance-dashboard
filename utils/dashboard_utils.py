import streamlit as st
import pandas as pd
from io import BytesIO
import pandas as pd
from utils.constants import (
    time_frame_mapping,
    category_col_mapping,
)
import streamlit_shadcn_ui as ui
from streamlit_extras.mention import mention


def display_contact_info():
    with st.sidebar:
        st.divider()
        st.markdown(
            """
        Get in touch:
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
    day_start, day_end = ui.date_picker(
        key="date_picker",
        mode="range",
        label="Selected Range",
        default_value=first_and_last_date,
    )
    return day_start, day_end


def display_get_transactions_file(example_file=None):
    """Displays the file uploader and returns the uploaded file."""
    with st.sidebar:
        uploaded_file = st.file_uploader(
            "Upload the transactions.", key="transactions_file"
        )
        if example_file:
            st.download_button(
                label="Download example transactions file",
                data=example_file,
                file_name="example_transactions_file.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
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


def display_get_configuration_file(example_file=None):
    """Displays the file uploader and returns the uploaded file."""
    with st.sidebar:
        uploaded_file = st.file_uploader("Upload the configuration file.", key="config")
        if example_file:
            # Create a download button
            st.download_button(
                label="Download example configuration file",
                data=example_file,
                file_name="example_dashboard_config.yaml",
                mime="application/x-yaml",
            )
    return uploaded_file


# Function to convert DataFrame to Excel
def df_to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, index=False, sheet_name="Sheet1")
    writer.close()
    processed_data = output.getvalue()
    return processed_data
