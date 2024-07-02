from polars.dataframe import DataFrame
import polars as pl
from typing import List
from utils.constants import (
    amount_col,
    source_col,
    type_col,
)
import streamlit as st


class CalculateUtils:
    def __init__(self):
        pass

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
        st.write(df.group_by([source_col, time_frame_col]))
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
