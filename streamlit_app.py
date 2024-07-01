import streamlit as st

categorize_page = st.Page(
    "categorize_page.py",
    title="Categorize Transactions",
    icon=":material/assignment_turned_in:",
)
dashboard_page = st.Page(
    "dashboard_page.py", title="Dashboard", icon=":material/bar_chart_4_bars:"
)

pg = st.navigation([dashboard_page, categorize_page])
pg.run()
