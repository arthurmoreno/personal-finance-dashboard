import streamlit as st
from utils.constants import paths
from utils.dashboard_utils import display_contact_info, read_config
from utils.app_utils import maincss
import os
from utils.firebasehandler import FirebaseHandler
import extra_streamlit_components as stx


st.set_page_config(
    layout="wide",
)
maincss("main.css")
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

firebaseConfig = {
    "apiKey": st.secrets["API_KEY"],
    "authDomain": st.secrets["AUTH_DOMAIN"],
    "projectId": st.secrets["PROJECT_ID"],
    "databaseURL": st.secrets["DATABASE_URL"],
    "storageBucket": st.secrets["STORAGE_BUCKET"],
    "messagingSenderId": st.secrets["MESSAGING_SENDER_ID"],
    "appId": st.secrets["APP_ID"],
    "measurementId": st.secrets["MEASUREMENT_ID"],
}


if "AgGrid_i" not in st.session_state:  # Needed to reload the AgGrid
    st.session_state.AgGrid_i = 0
if "config" not in st.session_state:  # Set config to the default config
    st.session_state.config = read_config(paths["default_dashboard_config"])
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
if st.session_state.cookie_manager.get(cookie="user_logged_in"):
    handle = (
        st.session_state.firebase.db.child(
            st.session_state.cookie_manager.get(cookie="user")["localId"]
        )
        .child("Handle")
        .get()
        .val()
    )
    st.sidebar.write(f"Hi {handle} 👋")

# DEBUG
# st.sidebar.write("config:", st.session_state.config)
# st.sidebar.write("cookies:", cookies)

pg = st.navigation(
    [dashboard_page, dashboard_settings, categorize_page, manage_account]
)
pg.run()
