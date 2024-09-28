import extra_streamlit_components as stx
import streamlit as st

from firebase import FirebaseHandler
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

manage_account = st.Page(
    "app_pages/manage_account.py",
    title="Manage account",
    icon=":material/person:",
)

privacy_policy = st.Page(
    "app_pages/privacy_policy.py",
    title="Privacy policy",
    icon=":material/lock:",
)

firebaseConfig = {
    "apiKey": st.secrets["config"]["apiKey"],
    "authDomain": st.secrets["config"]["authDomain"],
    "databaseURL": st.secrets["config"]["databaseURL"],
    "storageBucket": st.secrets["config"]["storageBucket"],
    "serviceAccount": {
        "type": st.secrets["serviceAccount"]["type"],
        "project_id": st.secrets["serviceAccount"]["project_id"],
        "private_key_id": st.secrets["serviceAccount"]["private_key_id"],
        "private_key": st.secrets["serviceAccount"]["private_key"],
        "client_email": st.secrets["serviceAccount"]["client_email"],
        "client_id": st.secrets["serviceAccount"]["client_id"],
        "auth_uri": st.secrets["serviceAccount"]["auth_uri"],
        "token_uri": st.secrets["serviceAccount"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["serviceAccount"][
            "auth_provider_x509_cert_url"
        ],
        "client_x509_cert_url": st.secrets["serviceAccount"]["client_x509_cert_url"],
    },
}


if "AgGrid_i" not in st.session_state:  # Needed to reload the AgGrid
    st.session_state.AgGrid_i = 0
if "dashboardconfig" not in st.session_state:  # Set config to the default config
    st.session_state.dashboardconfig = read_config(paths["default_dashboard_config"])
if "income_category_index" not in st.session_state:  # needed for the pieplot
    st.session_state.income_category_index = None
if "firebase" not in st.session_state:
    st.session_state.firebase = FirebaseHandler(firebaseConfig)
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
if "first_run_while_logged_in" not in st.session_state:
    st.session_state.first_run_while_logged_in = 0

if st.session_state.cookie_manager.get(cookie="user_logged_in"):
    st.session_state.first_run_while_logged_in = (
        st.session_state.first_run_while_logged_in + 1
    )
    user_id = st.session_state.cookie_manager.get(cookie="user")["localId"]
    handle = st.session_state.firebase.db.child(user_id).child("Handle").get().val()
    st.sidebar.write(f"Hi {handle} 👋")

if st.session_state.first_run_while_logged_in == 1:
    fetched_CategorizationConfig = st.session_state.firebase.read_file(
        user_id, "CategorizationConfig"
    )
    if fetched_CategorizationConfig is not None:
        st.session_state.config_to_categorize = fetched_CategorizationConfig

    fetched__subcategory_to_category = st.session_state.firebase.read_file(
        user_id, "_subcategory_to_category"
    )
    if fetched__subcategory_to_category is not None:
        st.session_state._subcategory_to_category = fetched__subcategory_to_category

if st.session_state.debug_mode:
    st.sidebar.write("cookies:", st.session_state.cookie_manager.get_all())
    st.sidebar.write("user:", st.session_state)
    st.sidebar.write(st.session_state.first_run_while_logged_in)
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
        manage_account,
        privacy_policy,
    ]
)
pg.run()
