import pandas as pd
import streamlit as st
from streamlit_javascript import st_javascript

from utils import (
    category_col,
    df_to_excel,
    display_get_transactions_file,
    get_checkbox_option,
    get_checkbox_options,
    get_color_picker_options,
    get_number_input_options,
    paths,
    read_config,
    save_config,
    source_col,
    subcategory_col,
    validate_dashboard_config_format,
    validate_data,
)


def display_header():
    st.title("Financial Dashboard Configuration")
    st.subheader("Transactions Data")


def _reset_dashboardconfig(user_id):
    st.session_state.dashboardconfig = read_config(paths["default_dashboard_config"])
    if st.session_state.cookie_manager.get(cookie="user_logged_in"):
        st.session_state.firebase.db.child(user_id).child("DashboardConfig").remove()


def _reload():
    """Reload the page (to make sure person is logged off, etc.)"""
    st_javascript(
        """
        window.location.reload()
        """,
        # key=str(st.session_state.reload_key),  # it needs a key to be reloaded
    )
    # st.session_state.reload_key = st.session_state.reload_key + 1
    _reload()


def handle_existing_data(user_id):
    df_fetched = st.session_state.firebase.read_file(user_id, "TransactionsData")
    if df_fetched is not None:
        with st.expander("Your categorized transactions."):
            st.dataframe(df_fetched)

        col1, col2 = st.columns([1, 7])
        with col1:
            if st.button("Delete data"):
                st.session_state.firebase.db.child(user_id).child(
                    "TransactionsData"
                ).remove()
                _reset_dashboardconfig(user_id)
                st_javascript("""window.location.reload()""")
        with col2:
            st.markdown("You can delete your data at any time and start over.")
    else:
        st.write("You do not have any data yet.")
    return df_fetched


def handle_file_upload(user_id, user_logged_in):
    next_step = (
        "Update" if (st.session_state.get("df_fetched") is not None) else "Upload"
    )
    col1, _, col2 = st.columns([2, 1, 2])

    with col1:
        example_categorized_transactions = pd.read_excel(
            paths["example_categorized_transactions"]
        )

        example_categorized_transactions = df_to_excel(example_categorized_transactions)

        file_path = display_get_transactions_file(
            f"{next_step} your transactions (.xlsx).", example_categorized_transactions
        )
    st.info(
        "The transactions should be structured like this:",
        icon="ℹ️",
    )
    st.dataframe(pd.read_excel(paths["categorized_data_structure"]))

    with col2:
        if st.button(f"{next_step} the file."):
            if file_path:
                df_fetched = pd.read_excel(file_path)
                df_fetched["DATE"] = df_fetched["DATE"].astype(str)
                if "TAG" in df_fetched.columns:  # TODO dont hardcod
                    df_fetched["TAG"] = df_fetched["TAG"]
                df_fetched = df_fetched.fillna("")
                # we should probably not validate twice
                validate_data(df_fetched)
                st.session_state.cookie_manager.set("file_exists", True, "file_exists")
                if user_logged_in:
                    st.session_state.firebase.upload_file(
                        df_fetched.to_dict(orient="records"),
                        user_id,
                        "TransactionsData",
                    )
                return df_fetched
            else:
                st.error("Please upload a file.")
        else:
            return None


def display_reset_dashboardconfig_button(user_id):
    # Allow the user to reset the value of t he config to the default one.
    # Sometimes the configs can also give errors, this will solve these errors.
    # These errors can happen if the user changes the config, but does not
    # update the data.
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Reset config"):
            _reset_dashboardconfig(user_id)

            with col2:
                st.success("Config reset.")
    with col2:
        st.markdown(
            """You can reset your config at any time and start over.
            This is also useful if you upload new data that is not compatible with the current config."""
        )


def handle_income_category_selection(categories, config):
    # The user is free to asign any category to be their "income" category
    # The subcategories from these category will be used to construct the pieplot
    # In the default config we already suggest a category "INCOME".
    # If this is not a category of the user, then show them their first category
    # as derived by the income_category_index
    if "income_category" in config:
        if config["income_category"] not in categories:
            st.session_state.income_category_index = 0
        else:
            st.session_state.income_category_index = categories.index(
                config["income_category"]
            )
    else:
        st.session_state.income_category_index = 0

    return st.selectbox(
        "Income category",
        options=categories,
        index=st.session_state.income_category_index,
    )


def display_config_options(user_id):
    df = st.session_state.df_fetched
    config = st.session_state.dashboardconfig

    categories = sorted(df[category_col].unique())
    sources = sorted(df[source_col].unique()) + ["Total"]

    st.header("General Settings")
    display_reset_dashboardconfig_button(user_id)

    config["display_data"] = st.checkbox("Display transactions", value=True)
    config["currency"] = st.text_input(
        "Currency symbol", value=config.get("currency", ""), max_chars=3
    )

    st.header("Chart Settings")
    config["hidden_categories_from_barplot"] = get_checkbox_options(
        categories, config, "hidden_categories_from_barplot"
    )

    st.subheader("Lineplot Colors")
    config["random_lineplot_colors"] = get_checkbox_option(
        "Random colors", config, "random_lineplot_colors"
    )
    config["lineplot_colors"] = (
        {}
        if config["random_lineplot_colors"]
        else get_color_picker_options(sources, config, "lineplot_colors")
    )
    st.subheader("Lineplot Width")
    config["lineplot_width"] = get_number_input_options(
        sources,
        value=3,
        min_value=1,
        max_value=10,
        config=config,
        config_name="lineplot_width",
    )

    st.subheader("Category Settings")
    config["income_category"] = handle_income_category_selection(categories, config)

    st.subheader("Pieplot Colors")
    income_sources = get_income_sources(df, config["income_category"])
    config["pieplot_colors"] = get_color_picker_options(
        income_sources, config, "pieplot_colors"
    )

    st.header("Financial Goals")
    config["goals"] = get_number_input_options(
        categories,
        value=None,
        min_value=0,
        max_value=None,
        config=config,
        config_name="goals",
    )
    config["goals"] = {k: v for k, v in config["goals"].items() if v is not None}

    validate_dashboard_config_format(config)
    return config


def get_income_sources(df, income_category):
    return sorted(df[df[category_col] == income_category][subcategory_col].unique())


display_header()
user_logged_in = st.session_state.cookie_manager.get(cookie="user_logged_in")
if user_logged_in:
    # Read the data the user has stored in the database. If there is no data yet,
    # this will be None
    user_id = st.session_state.cookie_manager.get(cookie="user")["localId"]
    df_fetched = handle_existing_data(user_id)
    if df_fetched is not None:
        st.session_state.df_fetched = df_fetched
else:
    user_id = None
    df_fetched = None

uploaded_df = handle_file_upload(user_id, user_logged_in)
if uploaded_df is not None:
    st.session_state.df_fetched = uploaded_df
if st.session_state.df_fetched is not None:
    validate_data(st.session_state.df_fetched)
    if user_logged_in:
        st.session_state.dashboardconfig = st.session_state.firebase.read_file(
            user_id, "DashboardConfig"
        )
        if st.session_state.dashboardconfig is None:
            st.session_state.dashboardconfig = read_config(
                paths["default_dashboard_config"]
            )
    else:
        st.session_state.dashboardconfig = read_config(
            paths["default_dashboard_config"]
        )
    updated_config = display_config_options(user_id)
    save_config(updated_config, user_id, "DashboardConfig")
