import streamlit as st
from utils.dashboard_utils import (
    display_get_transactions_file,
    df_to_excel,
    get_checkbox_options,
    get_color_picker_options,
    get_number_input_options,
)
import pandas as pd
from utils.constants import (
    example_categorized_transactions_path,
    exaple_dashboard_config_path,
    category_col,
    subcategory_col,
    source_col,
)

# Get example transactions data
example_transactions_data = df_to_excel(
    pd.read_excel(example_categorized_transactions_path)
)

# Get example config
with open(
    exaple_dashboard_config_path,
    "r",
) as file:
    yaml_data = file.read()

st.title("Financial Dashboard Configuration")
st.divider()

st.subheader("Tramsactions Data")

if st.session_state.user_logged_in:
    pass
    # TODO after firebase integration

if not st.session_state.user_logged_in:
    col1, _, col2 = st.columns([2, 1, 2])
    st.write("User is not logged in")
    with col1:
        file_path = display_get_transactions_file(
            title="Upload categorized transactions (.xlsx)",
            example_file=example_transactions_data,
        )
    with col2:
        submit = st.button("Upload the file.")
        if submit:
            df_fetched = pd.read_excel(file_path)
            st.session_state.file = df_fetched

st.divider()

if st.session_state.file is not None:
    categories = sorted(st.session_state.file[category_col].unique())
    subcategories = sorted(st.session_state.file[subcategory_col].unique())
    sources = sorted(st.session_state.file[source_col].unique())

    st.header("General Settings")
    display_data = st.checkbox("Display transactions", value=True)
    currency = st.text_input("Currency symbol", value="€", max_chars=3)

    st.header("Chart Settings")
    st.sidebar.write(st.session_state.config)
    st.subheader("Hidden Categories from Barplot")
    hidden_categories_from_barplot = get_checkbox_options(
        categories, st.session_state.config, "hidden_categories_from_barplot"
    )

    st.subheader("Lineplot Colors")
    lineplot_colors = get_color_picker_options(
        sources, st.session_state.config, "lineplot_colors"
    )
    st.subheader("Lineplot Width")
    lineplot_width = get_number_input_options(
        sources,  # todo: add "all"
        value=3,
        min_value=1,
        max_value=10,
        config=st.session_state.config,
        config_name="lineplot_width",
    )
    st.header("Category Settings")

    income_category = st.selectbox(
        "Income category",
        options=categories,
        index=st.session_state.income_category_index,
    )

    pieplot_colors = None  # TODO: why is this neccesary?
    if income_category:
        st.session_state.income_category_index = categories.index(income_category)
        st.subheader("Pieplot Colors")
        income_sources = sorted(
            st.session_state.file[
                st.session_state.file[category_col] == income_category
            ][subcategory_col].unique()
        )
        pieplot_colors = get_color_picker_options(
            income_sources, st.session_state.config, "pieplot_colors"
        )

    st.header("Financial Goals")
    goals = get_number_input_options(
        categories,
        value=100,
        min_value=0,
        max_value=None,
        config=st.session_state.config,
        config_name="goals",
    )
    if st.button("Save Configuration"):
        config = {
            "display_data": display_data,
            "currency": currency,
            "hidden_categories_from_barplot": hidden_categories_from_barplot,
            "pieplot_colors": pieplot_colors,
            "lineplot_colors": lineplot_colors,
            "lineplot_width": lineplot_width,
            "income_category": income_category,
            "goals": goals,
        }
        st.success("Configuration saved! (Not really, this is just a demonstration)")
        st.subheader("Entered Configuration:")
        st.session_state.config = config

        if st.session_state.user_logged_in:
            pass
            # TODO after firebase integration
