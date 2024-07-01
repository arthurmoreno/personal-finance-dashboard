import streamlit as st

categorize_page = st.Page(
    "categorize_page.py",
    title="Categorize Transactions",
    icon=":material/assignment_turned_in:",
)
dashboard_page = st.Page(
    "dashboard_page.py", title="Dashboard", icon=":material/bar_chart_4_bars:"
)

st.markdown(
    """
    <style>
    .main > div {
            padding-left: 10%;
            padding-right: 10%;
    }
    .main-header {
        font-size: 42px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 24px;
        text-align: center;
        color: #2E9BF5;
    }
    .intro-text {
        font-size: 18px;
        margin-bottom: 5px;
        margin-top: 20px;
    }
    .section-header {
        font-size: 28px;
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 10px;
    }
    .feature-list, .custom-list {
        font-size: 18px;
    }
    .feature-list li, .custom-list li {
        margin-bottom: 5px;
    }
    .subsection-header {
        font-size: 22px;
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
pg = st.navigation([dashboard_page, categorize_page])
pg.run()
