amount_col = "AMOUNT"
date_col = "DATE"
source_col = "SOURCE"
type_col = "TYPE"
time_frame_mapping = {
    "Weekly": "YEAR_WEEK",
    "Daily": "DATE",
    "Monthly": "YEAR_MONTH",
}
category_col_mapping = {
    "Category": "CATEGORY",
    "Subcategory": "SUBCATEGORY",
}

sample_config_path = "sample_resources/sample_dashboard_config.yml"
data_structure_path = "sample_resources/data_structure.xlsx"
sample_transactions_path = "sample_resources/transactions_in_categories_example.xlsx"

home_title = "Personal Finance Dashboard"
home_introduction = "Welcome to a streamlit based personal finance dashboard. Here,\
    you can get a visual representation of your finances over time by providing your\
    transaction history."
home_privacy = "This application is hosted on Streamlit Cloud. Terms and services of\
    Streamlit Cloud therefore apply."
home_transactions_info = "You will need to provide an excel file (.xlsx) in the sidebar structured like this:"
home_config_info = "You can optionally provide a configuration file (.yml) in the sidebar structured like this:"
