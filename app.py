import streamlit as st
import yaml
from utils.constants import paths
from utils.dashboard_utils import (
    display_contact_info,
)

st.set_page_config(
    layout="wide",
)
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


def maincss(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


maincss("main.css")

# Needed to reload the AgGrid
if "AgGrid_i" not in st.session_state:
    st.session_state.AgGrid_i = 0
if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False
if "config" not in st.session_state:
    with open(paths["default_dashboard_config"]) as stream:
        try:
            st.session_state.config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
if "file" not in st.session_state:
    st.session_state.file = None
if "income_category_index" not in st.session_state:
    st.session_state.income_category_index = None

display_contact_info()
pg = st.navigation([dashboard_page, dashboard_settings, categorize_page])
pg.run()
