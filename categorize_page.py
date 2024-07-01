import streamlit as st
import yaml
import pandas as pd
from utils.parse_data import TransactionProcessor
from st_aggrid import JsCode, GridOptionsBuilder, AgGrid
from utils.dashboard_utils import (
    display_get_transactions_file,
    display_get_configuration_file,
    display_contact_info,
    df_to_excel,
)
from utils.constants import (
    example_config_path,
    example_transactions_path,
    data_structure_path,
)

if "i" not in st.session_state:
    st.session_state.i = 0

# Let user upload transactions data
file_path = display_get_transactions_file()
uploaded_config = display_get_configuration_file()
display_contact_info()

if (uploaded_config is not None) & (file_path is not None):
    st.markdown(
        """
        <ul class="feature-list">
            <li>Categories and subcategories have been assgined to all your transactions. </li>
            <li>You can now overwrite any categories and subcategories that got assigned incorrectly. </li>
            <li>Some transactions, highlighted in <strong><span style="color: red; font-styl:bold">red</span></strong>, have not been assigned to any category. </li>
            <li>Consider expanding the configuration file to include these transactions, or manually edit them yourself. </li>
            <li>It is recommended to only change the subcategory and press <em>'Fill in Category'</em> to update the category based on the configuration file. </li>
        </ul>""",
        unsafe_allow_html=True,
    )
    config = yaml.safe_load(uploaded_config)
    org_data = pd.read_excel(file_path)
    processor = TransactionProcessor(config)

    if "updated_df" not in st.session_state or st.session_state.updated_df is None:
        categorized_data = processor.map_categories(org_data)
        processor.validate_data(categorized_data)
        categorized_data = processor.remove_columns(categorized_data)
    else:
        categorized_data = st.session_state.updated_df

    grid_builder = GridOptionsBuilder.from_dataframe(categorized_data)
    grid_builder.configure_default_column(editable=True, flex=1)
    for c in ["CATEGORY", "SUBCATEGORY"]:
        grid_builder.configure_column(
            c,
            cellEditor="agSelectCellEditor",
            cellEditorParams={
                "values": sorted(list(set(categorized_data[c]))),
            },
        )
    grid_options = grid_builder.build()
    grid_options["defaultColDef"]["cellStyle"] = JsCode(
        r"""
        function(cellClassParams) {
            if (cellClassParams.data.CATEGORY == 'UNKNOWN' || cellClassParams.data.SUBCATEGORY == 'UNKNOWN') {
                return {'background-color': 'red'}
            }
            return {};
            }
    """
    )
    res = AgGrid(
        data=categorized_data,
        gridOptions=grid_options,
        allow_unsafe_jscode=True,
        key=f"grid_{st.session_state.i}",
    )

    if st.button("Fill in category"):
        st.session_state.i += 1
        categorized_data = res["data"]
        categorized_data = processor.map_categories(categorized_data, False)
        st.session_state.updated_df = categorized_data
        st.dataframe(categorized_data)
        st.rerun()

    categorized_data_excel = df_to_excel(categorized_data)
    # Create a download button
    st.download_button(
        label="Download categorized transactions",
        data=categorized_data_excel,
        file_name="categorized_transactions.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:

    margins_css = st.markdown(
        """
    <style>
        .main > div {
            padding-left: 10%;
            padding-right: 10%;
        }
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
        <div class="main-header">Categorize Transactions:</div>
        <div class="sub-header">Take Control of Your Finances</div>
        <div class="intro-text">Welcome to a Streamlit-based personal finance dashboard. This intuitive dashboard is designed to give you a visual representation of your finances over time, empowering you to make informed decisions and achieve your financial goals.</div>
        <div class="section-header">Privacy</div>
        <div class="intro-text">This application is hosted on Streamlit Cloud. Terms of service of Streamlit Cloud therefore apply.</div>
        <div class="section-header">Requirements</div>
        <div class="subsection-header">Transactions data</div>
        """,
        unsafe_allow_html=True,
    )
    st.warning(
        '👈 Upload an excel (.xlsx) file in the sidebar or click *"Download example transactions"* to get started!'
    )
    st.info(
        "In order to categorize your transactions, only a description is sufficient. However, if you would like to use the dashboard later on, it is recommend to have an excel file structured like this:",
        icon="ℹ️",
    )

    example_transactions_data = df_to_excel(pd.read_excel(example_transactions_path))

    # Create a download button
    st.download_button(
        label="Download example transactions file",
        data=example_transactions_data,
        file_name="example_transactions_file.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    data_structure = pd.read_excel(data_structure_path)
    st.dataframe(data_structure)

    st.markdown(
        '<div class="subsection-header">Configuration file</div>',
        unsafe_allow_html=True,
    )
    st.warning(
        '👈 Upload a configuration file (.yml) in the sidebar or click *"Download example configuration file"* to get started!'
    )
    st.info(
        "This file will contain the rules for categorizing your transactions. Every transaction should only have 1 subcategory. Every subcategory should have exactly 1 category.",
        icon="ℹ️",
    )

    with open(
        example_config_path,
        "r",
    ) as file:
        yaml_data = file.read()
    # Create a download button
    st.download_button(
        label="Download example configuration file",
        data=yaml_data,
        file_name="test.yml",
        mime="application/x-yaml",
    )

    st.code(yaml_data, language="yml")
