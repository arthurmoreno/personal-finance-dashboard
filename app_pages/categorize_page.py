import streamlit as st
import yaml
import pandas as pd
from utils.parse_data import TransactionProcessor
from st_aggrid import JsCode, GridOptionsBuilder, AgGrid
from utils.dashboard_utils import (
    display_get_transactions_file,
    display_get_configuration_file,
    df_to_excel,
)
from utils.constants import paths
from utils.data_utils import (
    validate_config_format,
    MappingConfigData,
)

# Let user upload their configuration file
with open(
    paths["example_categories_mapping_config"],
    "r",
) as file:
    example_categories_mapping_config_data = file.read()

# Let user upload transactions data
example_transactions_data = df_to_excel(pd.read_excel(paths["example_transactions"]))
cols = st.columns(2)
with cols[0]:
    file_path = display_get_transactions_file(
        title="Upload transactions (.xlsx)", example_file=example_transactions_data
    )
with cols[1]:
    config_path = display_get_configuration_file(
        title="Upload categorization mapping (.yml)",
        example_file=example_categories_mapping_config_data,
    )


if (config_path is not None) & (file_path is not None):
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
    config = yaml.safe_load(config_path)
    validate_config_format(config, MappingConfigData)
    org_data = pd.read_excel(file_path)
    processor = TransactionProcessor(config)

    if "updated_df" not in st.session_state or st.session_state.updated_df is None:
        categorized_data = processor.map_and_validate_categories(org_data)
    else:
        categorized_data = st.session_state.updated_df

    grid_builder = GridOptionsBuilder.from_dataframe(categorized_data)
    grid_builder.configure_default_column(editable=True, flex=1)
    for c in ["CATEGORIES", "SUBCATEGORIES"]:
        col_name = {"CATEGORIES": "CATEGORY", "SUBCATEGORIES": "SUBCATEGORY"}[c]
        grid_builder.configure_column(
            col_name,
            cellEditor="agSelectCellEditor",
            cellEditorParams={
                "values": sorted(set(config[c].keys())),
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
        key=f"grid_{st.session_state.AgGrid_i}",
    )

    if st.button("Fill in category"):
        st.session_state.AgGrid_i += 1
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
    st.markdown(
        """
        <div class="main-header">Categorize Transactions</div>
        <div class="sub-header">Take Control of Your Finances</div>
        <div class="section-header">Requirements</div>
        <div class="subsection-header">Transactions data</div>
        """,
        unsafe_allow_html=True,
    )
    st.warning(
        '☝️ Upload an excel (.xlsx) file or click *"Download example"* to get started!'
    )
    st.info(
        "In order to categorize your transactions, only a description is sufficient. However, if you would like to use the dashboard later on, it is recommend to have an excel file structured like this:",
        icon="ℹ️",
    )

    data_structure = pd.read_excel(paths["data_structure"])
    st.dataframe(data_structure)

    st.markdown(
        '<div class="subsection-header">Configuration file</div>',
        unsafe_allow_html=True,
    )
    st.warning(
        '☝️ Upload a configuration file (.yml) or click *"Download example"* to get started!'
    )
    st.info(
        "This file will contain the rules for categorizing your transactions. Every transaction should only have 1 subcategory. Every subcategory should have exactly 1 category.",
        icon="ℹ️",
    )

    st.code(example_categories_mapping_config_data, language="yml")
