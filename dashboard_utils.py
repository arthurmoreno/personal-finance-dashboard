import streamlit as st
import pandas as pd
from io import BytesIO
import pandas as pd
import polars as pl
from constants import sample_transactions_path, data_structure_path, sample_config_path


def display_get_transactions_file():
    """Displays the file uploader and returns the uploaded file."""
    with st.sidebar:
        uploaded_file = st.file_uploader(
            "Upload the transactions.", key="transactions_file"
        )
    return uploaded_file


def display_get_configuration_file():
    """Displays the file uploader and returns the uploaded file."""
    with st.sidebar:
        uploaded_file = st.file_uploader("Upload the configuration file.", key="config")
    return uploaded_file


def display_home():
    home_title = "Personal Finance Dashboard"
    home_introduction = "Welcome to a streamlit based personal finance dashboard. Here,\
        you can get a visual representation of your finances over time by providing your\
        transaction history."
    home_privacy = "This application is hosted on Streamlit Cloud. Terms and services of\
        Streamlit Cloud therefore apply."
    home_info = "You will need to provide an excel file (.xlsx) in the sidebar structured like this:"
    home_config_info = "You will need to provide a configuration file (.yml) in the sidebar structured like this:"

    st.markdown("<style>#MainMenu{visibility:hidden;}</style>", unsafe_allow_html=True)

    # st.title(home_title)
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
    st.info(home_info, icon="ℹ️")
    example_transactions_data = pl.read_excel(sample_transactions_path).to_pandas()

    # Function to convert DataFrame to Excel
    def to_excel(df):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine="xlsxwriter")
        df.to_excel(writer, index=False, sheet_name="Sheet1")
        writer.close()
        processed_data = output.getvalue()
        return processed_data

    # Convert DataFrame to Excel
    example_transactions_data = to_excel(example_transactions_data)

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
