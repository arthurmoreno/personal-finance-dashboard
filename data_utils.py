from polars.dataframe import DataFrame
import polars as pl
import streamlit as st
from typing import List
from plots import PlotUtils
from constants import (
    amount_col,
    date_col,
    source_col,
    type_col,
    time_frame_mapping,
    category_col_mapping,
)
import streamlit_shadcn_ui as ui


class FinanceDashboard:
    def __init__(self, config_file):
        self.data = None
        self.all_sources = None
        self.first_and_last_date = None
        self.PlotUtils = PlotUtils(config_file=config_file)

    def calculate_transactions_per_category(
        self, df: DataFrame, category_col: str, time_frame_col: str
    ):
        """Calculates the transactions per category."""
        df = (
            df.groupby(time_frame_col, category_col)
            .agg(pl.sum(amount_col).alias(amount_col))
            .sort(category_col, time_frame_col)
            .select(time_frame_col, category_col, amount_col)
        )
        return df

    def calculate_income_outcome(
        self, df: DataFrame, source: List[str], time_frame_col: str, category_col: str
    ):
        """Calculates the income and outcome balance for a given source over time"""
        distinct_time = df.select(time_frame_col).unique()
        distinct_type = df.select(type_col).unique()
        distinct_time_type = distinct_type.join(distinct_time, how="cross")
        df = df.filter(df[source_col].is_in(source))
        df = df.filter(df[category_col] != "TRANSFERS")

        income_outcome = (
            distinct_time_type.join(
                df.groupby(time_frame_col, type_col).agg(
                    pl.sum(amount_col).alias(amount_col)
                ),
                on=[time_frame_col, type_col],
                how="left",
            )
            .sort(type_col, time_frame_col)
            .with_columns(AMOUNT=pl.col(amount_col).abs())
            .fill_null(0)
            .select(time_frame_col, type_col, amount_col)
        )

        return income_outcome

    def calculate_net_value(self, df: DataFrame, time_frame_col: str):
        """Calculates the net value for all sources over time."""
        distinct_sources = df.select(source_col).unique()
        distinct_time = df.select(time_frame_col).unique()

        net_value_per_source = (
            distinct_sources.join(distinct_time, how="cross")
            .join(
                df.groupby([source_col, time_frame_col])
                .agg(pl.sum(amount_col).alias("NET_VALUE"))
                .sort(source_col, time_frame_col)
                .with_columns(
                    pl.cum_sum("NET_VALUE")
                    .sort_by(time_frame_col, descending=False)
                    .over(source_col)
                    .alias("NET_VALUE")
                ),
                on=[source_col, time_frame_col],
                how="left",
            )
            .sort([source_col, time_frame_col])
            .with_columns(pl.exclude(source_col).forward_fill().over(source_col))
            .with_columns(
                (
                    pl.col("NET_VALUE") - pl.col("NET_VALUE").shift(1).over(source_col)
                ).alias("ToT")
            )
            .fill_null(0)
            .select(time_frame_col, "NET_VALUE", source_col, "ToT")
        )

        net_value_total = (
            net_value_per_source.groupby(time_frame_col)
            .agg(pl.sum("NET_VALUE").alias("NET_VALUE"))
            .with_columns(pl.lit("Total").alias(source_col))
            .sort(time_frame_col)
            .fill_null(0)
            .with_columns(
                (
                    pl.col("NET_VALUE") - pl.col("NET_VALUE").shift(1).over(source_col)
                ).alias("ToT")
            )
            .fill_null(0)
            .select(time_frame_col, "NET_VALUE", source_col, "ToT")
        )

        net_value = pl.concat([net_value_total, net_value_per_source])

        return net_value

    def display_net_value(self, df, time_frame_col, all_sources):
        """Displays the net value as a line plot over time and as tiles."""
        net_value = self.calculate_net_value(df, time_frame_col)
        a, b = st.columns([6, 4])
        with a:
            self.PlotUtils.plot_net_value_line_plot(net_value, time_frame_col)
        with b:
            self.PlotUtils.plot_net_value_tiles(net_value, time_frame_col, all_sources)

    def display_tabs(self):
        """Displays the tabs for the time frame, source and category and return their value."""

        def create_tabs(mapping):
            # Key is arbitrary here.
            selected = ui.tabs(
                options=mapping.keys(),
                default_value=list(mapping.keys())[0],
                key=list(mapping.keys())[0],
            )
            selected_col = mapping.get(selected)

            return selected_col

        tabs = st.columns([3, 3, 6])
        with tabs[0]:
            time_frame_col = create_tabs(time_frame_mapping)
        with tabs[1]:
            category_col = create_tabs(category_col_mapping)
        return time_frame_col, category_col

    def display_sources(self, all_sources):
        sources = st.multiselect(
            label="",
            options=all_sources,
            default=all_sources,
        )
        return sources

    def display_date_picker(self, first_and_last_date):
        """Displays the date picker and returns the selected dates."""
        day_start, day_end = ui.date_picker(
            key="date_picker",
            mode="range",
            label="Selected Range",
            default_value=first_and_last_date,
        )
        return day_start, day_end

    def display_data(self, df):
        """Displays the transaction data."""
        with st.expander("Data Preview"):
            st.dataframe(df)

    def get_all_sources(self, df):
        """Returns a list of all sources available in the data."""
        return sorted(df.select(source_col).unique().to_series().to_list())

    def display_income_outcome(self, df, source, time_frame_col, category_col):
        """Displays the income and outcome for the selected source over time as a lineplot."""
        income_outcome = self.calculate_income_outcome(
            df, source, time_frame_col, category_col
        )
        self.PlotUtils.plot_lineplot_income_outcome(income_outcome, time_frame_col)

    def display_transactions_per_category(self, df, category_col, time_frame_col):
        """Displays the transactions per category over time as a barplot."""
        transactions_per_category = self.calculate_transactions_per_category(
            df, category_col, time_frame_col
        )
        self.PlotUtils.plot_transactions_per_category(
            transactions_per_category, category_col, time_frame_col
        )

    def get_first_last_date(self, df):
        """Returns the first and last date in the data. Used to set the date picker."""
        first_date = df.select(date_col).min().item()[0:10]
        last_date = df.select(date_col).max().item()[0:10]
        return first_date, last_date

    def filter_data(self, data, start_date, end_date):
        """Filters the data to the selected date range."""
        data = data.filter(
            (pl.col(date_col) >= start_date) & (pl.col(date_col) <= end_date)
        )
        return data

    def display_pieplot(self, df):
        data = (
            df.filter(pl.col("CATEGORY") == "INCOME")
            .group_by("SUBCATEGORY")
            .agg(pl.sum("AMOUNT").alias("AMOUNT"))
            .sort("SUBCATEGORY")
        )
        a = self.PlotUtils.plot_pieplot(data)
        return a
