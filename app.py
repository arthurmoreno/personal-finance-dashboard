import streamlit as st

st.set_page_config(
    layout="wide",
)
categorize_page = st.Page(
    "categorize_page.py",
    title="Categorize Transactions",
    icon=":material/assignment_turned_in:",
    url_path="categorize_transactions",
)
dashboard_page = st.Page(
    "dashboard_page.py", title="Dashboard", icon=":material/bar_chart_4_bars:"
)


def maincss(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


maincss("main.css")
pg = st.navigation([dashboard_page, categorize_page])
pg.run()
