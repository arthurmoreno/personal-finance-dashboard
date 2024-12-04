"""Some constants."""

amount_col = 'AMOUNT'
date_col = 'DATE'
source_col = 'SOURCE'
type_col = 'TYPE'
category_col = 'CATEGORY'
subcategory_col = 'SUBCATEGORY'
time_frame_mapping = {'Monthly': 'YEAR_MONTH', 'Weekly': 'YEAR_WEEK', 'Daily': 'DATE'}
category_col_mapping = {'Category': category_col, 'Subcategory': subcategory_col}
colors = ['#07004D', '#42E2B8', '#F3DFBF', '#2D82B7', '#EB8A90']
paths = {
    'default_dashboard_config': 'static/default_dashboard.yml',
    'categorized_data_structure': 'static/categorized/data_structure.xlsx',
    'example_categorized_transactions': 'static/categorized/transactions.xlsx',
    'example_transactions': 'static/raw/transactions.xlsx',
    'data_structure': 'static/raw/data_structure.xlsx',
    'example_categories_mapping_config': 'static/raw/categories_mapping.yml',
    'maincss': 'static/main.css',
}
