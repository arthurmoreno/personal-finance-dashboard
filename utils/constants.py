amount_col = "AMOUNT"
date_col = "DATE"
source_col = "SOURCE"
type_col = "TYPE"
category_col = "CATEGORY"
subcategory_col = "SUBCATEGORY"
time_frame_mapping = {
    "Weekly": "YEAR_WEEK",
    "Daily": "DATE",
    "Monthly": "YEAR_MONTH",
}
category_col_mapping = {
    "Category": category_col,
    "Subcategory": subcategory_col,
}

paths = {
    "default_dashboard_config": "default_dashboard.yml",
    "categorized_data_structure": "example_resources/categorized/data_structure.xlsx",
    "example_categorized_transactions": "example_resources/categorized/transactions.xlsx",
    "exaple_dashboard_config": "example_resources/categorized/dashboard.yml",
    "example_transactions": "example_resources/raw/transactions.xlsx",
    "data_structure": "example_resources/raw/data_structure.xlsx",
    "example_config": "example_resources/raw/categories_mapping.yml"
}
