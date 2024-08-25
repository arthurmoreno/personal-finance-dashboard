import streamlit as st
from utils.dashboard_utils import (
    display_get_transactions_file,
    get_checkbox_options,
    get_checkbox_option,
    get_color_picker_options,
    get_number_input_options,
    read_config,
)
import pandas as pd
from utils.constants import (
    paths,
    category_col,
    subcategory_col,
    source_col,
)
import time
from utils.data_utils import validate_data

st.title("Financial Dashboard Configuration")
st.subheader("Transactions Data")

if st.session_state.cookie_manager.get(cookie="user_logged_in"):
    # Read the data the user has stored in the database. If there is no data yet,
    # this will be None
    st.session_state.df_fetched = st.session_state.firebase.read_file(
        st.session_state.cookie_manager.get(cookie="user")["localId"],
        "TransactionsData",
    )
    if st.session_state.df_fetched is not None:
        # If there is data
        with st.expander("Your categorized transactions."):
            st.dataframe(st.session_state.df_fetched)

        click_button_section, text_section = st.columns([1, 7])
        with click_button_section:
            if st.button("Delete data"):
                time.sleep(1)
                st.session_state.firebase.db.child(
                    st.session_state.cookie_manager.get(cookie="user")["localId"]
                ).child("TransactionsData").remove()
                st.rerun()
        with text_section:
            st.markdown("You can delete your data at any time and start over.")
    else:
        st.write("You do not have any data yet.")

    load_file_section, _, click_button_section = st.columns([2, 1, 2])
    with load_file_section:
        if st.session_state.df_fetched is not None:
            next_step = "Update"  # Allow the user to Update the data
        else:
            next_step = "Upload"  # Allow the user to Upload the data
        file_path = display_get_transactions_file(
            title=f"{next_step} your transactions (.xlsx)."
        )
    with click_button_section:
        # With this button the data actually gets updated/ uploaded
        if st.button(f"{next_step} the file."):
            if file_path:
                # Read the excel data as a dataframe
                st.session_state.df_fetched = pd.read_excel(file_path)
                # Set this to true -- needed for other functions
                st.session_state.cookie_manager.set("file_exists", True, "file_exists")
                # Upload (overwrite) the new file to the database
                st.session_state.firebase.upload_file(
                    file_path,
                    st.session_state.cookie_manager.get(cookie="user")["localId"],
                    "TransactionsData",
                )
            else:
                # If they had not uploaded a file
                st.error("Please upload a file.")

    # Check if the user has a pre-existing config, and use that.
    latest_config = st.session_state.firebase.read_file(
        st.session_state.cookie_manager.get(cookie="user")["localId"], "Config"
    )
    if latest_config is not None:
        st.session_state.config = latest_config
else:
    # If user is not logged in, allow him to upload a file.
    # Updating the file is not needed, the user can just refresh their screen
    next_step = "Upload"
    load_file_section, _, click_button_section = st.columns([2, 1, 2])
    with load_file_section:
        file_path = display_get_transactions_file(
            title=f"{next_step} your transactions (.xlsx)."
        )
    with click_button_section:
        if st.button(f"{next_step} the file."):
            if file_path:
                # If a file exist, and the user uploads it:
                st.session_state.df_fetched = pd.read_excel(file_path)
                st.session_state.file_exists = True
                st.session_state.cookie_manager.set("file_exists", True, "file_exists")
            else:
                st.error("Please upload a file.")
st.divider()

# If there is actually an uploaded file, then show the configuration settings that
# the user can adjust.
if st.session_state.df_fetched is not None:
    validate_data(st.session_state.df_fetched)
    categories = sorted(st.session_state.df_fetched[category_col].unique())
    subcategories = sorted(st.session_state.df_fetched[subcategory_col].unique())
    sources = sorted(st.session_state.df_fetched[source_col].unique()) + ["Total"]
    st.header("General Settings")

    # Allow the user to reset the value of the config to the default one.
    # Sometimes the configs can also give errors, this will solve these errors.
    # These errors can happen if the user changes the config, but does not
    # update the data.
    click_button_section, text_section = st.columns([1, 4])
    with click_button_section:
        if st.button("Reset config"):
            # Reset the config by going back to the default value
            st.session_state.config = read_config(paths["default_dashboard_config"])

            # Also delete the config from the database (dirty fix for now like this)
            if st.session_state.cookie_manager.get(cookie="user_logged_in"):
                st.session_state.firebase.db.child(
                    st.session_state.cookie_manager.get(cookie="user")["localId"]
                ).child("Config").remove()
            with text_section:
                st.success("Config resetted.")
    with text_section:
        st.markdown(
            "You can reset your config at any time and start over. This is also useful if you upload new data that is not compatibale with the current config."
        )

    # The settings:
    display_data = st.checkbox("Display transactions", value=True)
    currency = st.text_input(
        "Currency symbol", value=st.session_state.config["currency"], max_chars=3
    )

    st.header("Chart Settings")

    st.subheader("Hidden Categories from Barplot")
    hidden_categories_from_barplot = get_checkbox_options(
        categories, st.session_state.config, "hidden_categories_from_barplot"
    )

    st.subheader("Lineplot Colors")
    select_random_lineplot_colors = get_checkbox_option(
        "Random colors", st.session_state.config, "random_lineplot_colors"
    )
    if select_random_lineplot_colors:
        # If the user want random colors we need to pass an empty dict
        lineplot_colors = {}
    else:
        # Otherwise let the user pick the colours
        lineplot_colors = get_color_picker_options(
            sources, st.session_state.config, "lineplot_colors"
        )

    st.subheader("Lineplot Width")
    lineplot_width = get_number_input_options(
        sources,
        value=3,
        min_value=1,
        max_value=10,
        config=st.session_state.config,
        config_name="lineplot_width",
    )

    st.subheader("Category Settings")
    # The user is free to asign any category to be their "income" category
    # The subcategories from these category will be used to construct the pieplot
    # In the default config we already suggest a category "INCOME".
    # If this is not a category of the user, then show them their first category
    # as derived by the income_category_index
    if "income_category" in st.session_state.config:
        if st.session_state.config["income_category"] not in categories:
            st.session_state.income_category_index = 0
        else:
            st.session_state.income_category_index = categories.index(
                st.session_state.config["income_category"]
            )
    else:
        st.session_state.income_category_index = 0

    income_category = st.selectbox(
        "Income category",
        options=categories,
        index=st.session_state.income_category_index,
    )

    st.subheader("Pieplot Colors")
    # Get the income sources (== the subcategories of the income category)
    income_sources = sorted(
        st.session_state.df_fetched[
            st.session_state.df_fetched[category_col] == income_category
        ][subcategory_col].unique()
    )
    # Set colours for these income sources
    pieplot_colors = get_color_picker_options(
        income_sources, st.session_state.config, "pieplot_colors"
    )

    st.header("Financial Goals")
    goals = get_number_input_options(
        categories,
        value=None,  # because we dont want a goal for all categories
        min_value=0,
        max_value=None,
        config=st.session_state.config,
        config_name="goals",
    )
    # Remove all categories without a goal
    goals = {k: v for k, v in goals.items() if v is not None}

    if st.button("Save Configuration"):
        st.session_state.config = {
            "display_data": display_data,
            "currency": currency,
            "hidden_categories_from_barplot": hidden_categories_from_barplot,
            "pieplot_colors": pieplot_colors,
            "random_lineplot_colors": select_random_lineplot_colors,
            "lineplot_colors": lineplot_colors,
            "lineplot_width": lineplot_width,
            "income_category": income_category,
            "goals": goals,
        }
        if st.session_state.cookie_manager.get(cookie="user_logged_in"):
            st.session_state.firebase.upload_file(
                st.session_state.config,
                st.session_state.cookie_manager.get(cookie="user")["localId"],
                "Config",
            )
        st.success("Configuration saved!")
        st.rerun()
