import pandas as pd
import streamlit as st
import yaml
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

from utils import (
    TransactionProcessor,
    df_to_excel,
    display_current_categorization_config_structure,
    display_get_configuration_file,
    display_get_transactions_file,
    paths,
    validate_categorize_mapping_config_format,
)

# Let user upload their configuration file
with open(
    paths["example_categories_mapping_config"],
    "r",
) as file:
    example_categories_mapping_config_data = file.read()

st.markdown(
    """
    <div class="main-header">Categorize Transactions</div>
    <div class="sub-header">Take Control of Your Finances</div>
    
    <p>To categorize your transactions:</p>
    <ul>
        <li>Use the 'Current Structure' tab to map rules to your desired categories and subcategories. A rule will search for a given word in the 'DESCRIPTION' column of your transactions.</li>
        <li>If you are logged in, save your current structure for a future session.</li>
        <li>If you are logged out, copy the configuration (.yml file). In a future session, simply upload this 
            file in the 'Upload Config' tab.</li>
        <li>Upload the transactions that you want to categorize in the 'Upload Transactions' tab.</li>
        <li>Download or modify your categorized transactions in the 'Categorize Transactions' tab.</li>
    </ul>
    """,
    unsafe_allow_html=True,
)


current_structure, upload_config, upload_transactions, categorize_transactions = (
    st.tabs(
        [
            "Current Structure",
            "Upload Config",
            "Upload Transactions",
            "Categorize Transactions",
        ]
    )
)

with current_structure:
    display_current_categorization_config_structure()
    col1, col2 = st.columns([5, 1])
    with col1.expander("Get current config (.yml):"):
        yaml_str = yaml.dump(st.session_state.config_to_categorize, sort_keys=False)
        st.code(yaml_str, language="yaml")
    user_logged_in = st.session_state.cookie_manager.get(cookie="user_logged_in")
    if user_logged_in:
        user_id = st.session_state.cookie_manager.get(cookie="user")["localId"]
        if col2.button("Save"):
            st.session_state.firebase.upload_file(
                st.session_state.config_to_categorize,
                user_id,
                "CategorizationConfig",
                rerun=False,
            )
            st.session_state.firebase.upload_file(
                st.session_state._subcategory_to_category,
                user_id,
                "_subcategory_to_category",
                rerun=False,
            )
            st.rerun()


with upload_config:
    st.info(
        """This file will contain the rules for categorizing your transactions.
        Every transaction should only have 1 subcategory.
        Every subcategory should have exactly 1 category.""",
        icon="ℹ️",
    )

    # Let user upload their configuration file
    with open(
        paths["example_categories_mapping_config"],
        "r",
    ) as file:
        example_categories_mapping_config_data = file.read()

    config_path = display_get_configuration_file(
        title="Upload categorization mapping (.yml)",
        example_file=example_categories_mapping_config_data,
    )
    if st.button("Upload the config"):
        if config_path:
            st.session_state.config_to_categorize = yaml.safe_load(config_path)
            # st.session_state.dashboardconfig["CATEGORIES"] = (
            #     st.session_state.dashboardconfig["CATEGORIES"]
            # )
            # st.session_state.dashboardconfig["SUBCATEGORIES"] = (
            #     st.session_state.dashboardconfig["SUBCATEGORIES"]
            # )
            for (
                category,
                subcategories,
            ) in st.session_state.config_to_categorize["CATEGORIES"].items():
                for subcategory in subcategories:
                    st.session_state._subcategory_to_category[subcategory] = category
            st.rerun()
        else:
            st.error("Please upload a configuration file.")
with upload_transactions:
    st.info(
        """In order to categorize your transactions, only a description is sufficient.
        However, if you would like to use the dashboard later on, it is recommend to have
        an excel file structured like this:""",
        icon="ℹ️",
    )

    data_structure = pd.read_excel(paths["data_structure"])
    st.dataframe(data_structure)
    # Let user upload transactions data
    example_transactions_data = df_to_excel(
        pd.read_excel(paths["example_transactions"])
    )
    file_path = display_get_transactions_file(
        title="Upload transactions (.xlsx)", example_file=example_transactions_data
    )
    if st.button("Upload the file."):
        if file_path:
            st.session_state.data_to_categorize = pd.read_excel(file_path)
        else:
            st.error("Please upload a transactions file.")

with categorize_transactions:
    if (st.session_state.config_to_categorize is not None) & (
        st.session_state.data_to_categorize is not None
    ):
        validate_categorize_mapping_config_format(st.session_state.config_to_categorize)
        st.markdown(
            """
            <ul class="feature-list">
                <li>Categories and subcategories have been assgined to all your transactions. </li>
                <li>You can now overwrite any categories and subcategories that got assigned incorrectly. </li>
                <li>Some transactions, highlighted in <strong>
                    <span style="color: red; font-styl:bold">red</span></strong>,
                    ave not been assigned to any category. </li>
                <li>Consider expanding the configuration file to include these transactions,
                or manually edit them yourself. </li>
                <li>It is recommended to only change the subcategory and press
                    <em>'Fill in Category'</em> to update the category based on the configuration file. </li>
            </ul>""",
            unsafe_allow_html=True,
        )
        processor = TransactionProcessor(st.session_state.config_to_categorize)

        if "updated_df" not in st.session_state or st.session_state.updated_df is None:
            categorized_data = processor.map_and_validate_categories(
                st.session_state.data_to_categorize
            )
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
                    "values": sorted(
                        set(st.session_state.config_to_categorize[c].keys())
                    ),
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
        st.write(
            "Please Upload a config/ create a current mapping structure and upload your transactions data first."
        )
