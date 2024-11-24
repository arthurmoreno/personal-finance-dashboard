import extra_streamlit_components as stx
import streamlit as st

from utils import display_contact_info, load_maincss, paths, read_config

st.set_page_config(
    layout="wide",
)
load_maincss(paths["maincss"])
display_contact_info()
st.sidebar.divider()

categorize_page = st.Page(
    "app_pages/categorize_page.py",
    title="Categorize Transactions",
    icon=":material/assignment_turned_in:",
    url_path="categorize_transactions",
)

dashboard_page = st.Page(
    "app_pages/dashboard_page.py", title="Dashboard", icon=":material/bar_chart_4_bars:"
)

dashboard_settings = st.Page(
    "app_pages/dashboard_settings.py",
    title="Dashboard Settings",
    icon=":material/bolt:",
)

privacy_policy = st.Page(
    "app_pages/privacy_policy.py",
    title="Privacy policy",
    icon=":material/lock:",
)


if "AgGrid_number" not in st.session_state:  # Needed to reload the AgGrid
    st.session_state.AgGrid_number = 0
if "dashboardconfig" not in st.session_state:  # Set config to the default config
    st.session_state.dashboardconfig = read_config(paths["default_dashboard_config"])
if "income_category_index" not in st.session_state:  # needed for the pieplot
    st.session_state.income_category_index = None
if "cookie_manager" not in st.session_state:
    st.session_state.cookie_manager = stx.CookieManager()
if "file_exists" not in st.session_state:
    st.session_state.file_exists = False
if "df_fetched" not in st.session_state:
    st.session_state.df_fetched = None
if "reload_key" not in st.session_state:
    st.session_state.reload_key = 0
if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False
if "data_to_categorize" not in st.session_state:
    st.session_state.data_to_categorize = None
if "_subcategory_to_category" not in st.session_state:
    st.session_state._subcategory_to_category = {}
if "config_to_categorize" not in st.session_state:
    st.session_state.config_to_categorize = {
        "CATEGORIES": {},
        "SUBCATEGORIES": {},
    }
if "updated_categorized_df" not in st.session_state:
    st.session_state.updated_categorized_df = None

if st.session_state.debug_mode:
    st.sidebar.write("cookies:", st.session_state.cookie_manager.get_all())
    st.sidebar.write(st.session_state._subcategory_to_category)
    st.sidebar.write(st.session_state.config_to_categorize)
    st.sidebar.write(st.session_state.dashboardconfig)
    testing_page = st.Page(
        "app_pages/testing.py",
        title="Testing",
        icon=":material/lock:",
    )


pg = st.navigation(
    [
        dashboard_page,
        dashboard_settings,
        categorize_page,
        privacy_policy,
    ]
)
pg.run()
