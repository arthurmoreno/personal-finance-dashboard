import yaml
from polars.dataframe import DataFrame
import polars as pl
import streamlit as st
from ui_components import date_picker, create_tabs
from typing import List
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


def get_config(config_path: str = "resources/dashboard_config.yml"):
    """Returns the config as a dictionary."""
    with open(config_path) as file:
        config = yaml.safe_load(file)
    return config


config = get_config()
AMOUNT_COL = config["col_names"]["AMOUNT_COL"]
DATE_COL = config["col_names"]["DATE_COL"]
SOURCE_COL = config["col_names"]["SOURCE_COL"]
TYPE_COL = config["col_names"]["TYPE_COL"]
TIME_FRAME_MAPPING = config["time_frame_mapping"]
SOURCE_MAPPING = config["source_mapping"]
CATEGORY_COL_MAPPING = config["category_col_mapping"]

# these imports should be here to avoid circular imports
from plots import (
    plot_net_value_line_plot,
    plot_net_value_tiles,
    plot_lineplot_income_outcome,
    plot_transactions_per_category,
    plot_pieplot,
)


def calculate_transactions_per_category(
    df: DataFrame, category_col: str, time_frame_col: str
):
    """Calculates the transactions per category."""
    df = (
        df.groupby(time_frame_col, category_col)
        .agg(pl.sum(AMOUNT_COL).alias(AMOUNT_COL))
        .sort(category_col, time_frame_col)
        .select(time_frame_col, category_col, AMOUNT_COL)
    )
    return df


def calculate_income_outcome(
    df: DataFrame, source: List[str], time_frame_col: str, category_col: str
):
    """Calculates the income and outcome balance for a given source over time"""
    distinct_time = df.select(time_frame_col).unique()
    distinct_type = df.select(TYPE_COL).unique()
    distinct_time_type = distinct_type.join(distinct_time, how="cross")
    df = df.filter(df[SOURCE_COL].is_in(source))
    df = df.filter(df[category_col] != "TRANSFERS")

    income_outcome = (
        distinct_time_type.join(
            df.groupby(time_frame_col, TYPE_COL).agg(
                pl.sum(AMOUNT_COL).alias(AMOUNT_COL)
            ),
            on=[time_frame_col, TYPE_COL],
            how="left",
        )
        .sort(TYPE_COL, time_frame_col)
        .with_columns(AMOUNT=pl.col(AMOUNT_COL).abs())
        .fill_null(0)
        .select(time_frame_col, TYPE_COL, AMOUNT_COL)
    )

    return income_outcome


def calculate_net_value(df: DataFrame, time_frame_col: str):
    """Calculates the net value for all sources over time."""
    distinct_sources = df.select(SOURCE_COL).unique()
    distinct_time = df.select(time_frame_col).unique()

    net_value_per_source = (
        distinct_sources.join(distinct_time, how="cross")
        .join(
            df.groupby([SOURCE_COL, time_frame_col])
            .agg(pl.sum(AMOUNT_COL).alias("NET_VALUE"))
            .sort(SOURCE_COL, time_frame_col)
            .with_columns(
                pl.cum_sum("NET_VALUE")
                .sort_by(time_frame_col, descending=False)
                .over(SOURCE_COL)
                .alias("NET_VALUE")
            ),
            on=[SOURCE_COL, time_frame_col],
            how="left",
        )
        .sort([SOURCE_COL, time_frame_col])
        .with_columns(pl.exclude(SOURCE_COL).forward_fill().over(SOURCE_COL))
        .with_columns(
            (pl.col("NET_VALUE") - pl.col("NET_VALUE").shift(1).over(SOURCE_COL)).alias(
                "ToT"
            )
        )
        .fill_null(0)
        .select(time_frame_col, "NET_VALUE", SOURCE_COL, "ToT")
    )

    net_value_total = (
        net_value_per_source.groupby(time_frame_col)
        .agg(pl.sum("NET_VALUE").alias("NET_VALUE"))
        .with_columns(pl.lit("Total").alias(SOURCE_COL))
        .sort(time_frame_col)
        .fill_null(0)
        .with_columns(
            (pl.col("NET_VALUE") - pl.col("NET_VALUE").shift(1).over(SOURCE_COL)).alias(
                "ToT"
            )
        )
        .fill_null(0)
        .select(time_frame_col, "NET_VALUE", SOURCE_COL, "ToT")
    )

    net_value = pl.concat([net_value_total, net_value_per_source])

    return net_value


def display_net_value(df, time_frame_col, all_sources):
    """Displays the net value as a line plot over time and as tiles."""
    net_value = calculate_net_value(df, time_frame_col)
    a, b = st.columns([6, 4])
    with a:
        plot_net_value_line_plot(net_value, time_frame_col)
    with b:
        plot_net_value_tiles(net_value, time_frame_col, all_sources)


def display_tabs():
    """Displays the tabs for the time frame, source and category and return their value."""
    tabs = st.columns([3, 3, 6])
    with tabs[0]:
        time_frame_col = create_tabs(TIME_FRAME_MAPPING)
    with tabs[1]:
        category_col = create_tabs(CATEGORY_COL_MAPPING)
    return time_frame_col, category_col


def display_sources(all_sources):
    valid_source_mapping = {
        key: SOURCE_MAPPING[key]
        for key in SOURCE_MAPPING
        if SOURCE_MAPPING[key] in all_sources
    }

    sources = st.multiselect(
        label="",
        options=valid_source_mapping.keys(),
        default=list(valid_source_mapping.keys()),
        key=list(valid_source_mapping.keys()),
    )
    return sources


def display_date_picker(first_and_last_date):
    """Displays the date picker and returns the selected dates."""
    day_start, day_end = date_picker(
        key="date_picker",
        mode="range",
        label="Selected Range",
        default_value=first_and_last_date,
    )
    return day_start, day_end


def display_data(df):
    """Displays the transaction data."""
    with st.expander("Data Preview"):
        st.dataframe(df)


def get_all_sources(df):
    """Returns a list of all sources available in the data."""
    return sorted(df.select(SOURCE_COL).unique().to_series().to_list())


def display_income_outcome(df, source, time_frame_col, category_col):
    """Displays the income and outcome for the selected source over time as a lineplot."""
    income_outcome = calculate_income_outcome(df, source, time_frame_col, category_col)
    plot_lineplot_income_outcome(income_outcome, time_frame_col)


def display_transactions_per_category(df, category_col, time_frame_col):
    """Displays the transactions per category over time as a barplot."""
    transactions_per_category = calculate_transactions_per_category(
        df, category_col, time_frame_col
    )
    plot_transactions_per_category(
        transactions_per_category, category_col, time_frame_col
    )


def get_data(path: str):
    """Returns the transaction data as a polars dataframe."""
    data = pl.read_excel(path)
    return data


def get_first_last_date(df):
    """Returns the first and last date in the data. Used to set the date picker."""
    first_date = df.select(DATE_COL).min().item()[0:10]
    last_date = df.select(DATE_COL).max().item()[0:10]
    return first_date, last_date


def filter_data(data, start_date, end_date):
    """Filters the data to the selected date range."""
    data = data.filter(
        (pl.col(DATE_COL) >= start_date) & (pl.col(DATE_COL) <= end_date)
    )
    return data


def display_pieplot(df):
    data = (
        df.filter(pl.col("CATEGORY") == "INCOME")
        .group_by("SUBCATEGORY")
        .agg(pl.sum("AMOUNT").alias("AMOUNT"))
        .sort("SUBCATEGORY")
    )
    a = plot_pieplot(data)
    return a


def display_get_file():
    """Displays the file uploader and returns the uploaded file."""
    with st.sidebar:
        uploaded_file = st.file_uploader("Choose a file")

    if uploaded_file is None:
        st.info("Upload a file through config", icon="ℹ️")
        st.stop()
    return uploaded_file
