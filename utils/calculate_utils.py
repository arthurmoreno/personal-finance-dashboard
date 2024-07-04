import polars as pl
from typing import List, Dict
from utils.constants import (
    amount_col,
    source_col,
    type_col,
)
import pandas as pd


class CalculateUtils:
    @staticmethod
    def calculate_transactions_per_category(
        df: pl.DataFrame, category_col: str, time_frame_col: str
    ):
        """Calculates the transactions per category."""
        df = (
            df.group_by(time_frame_col, category_col)
            .agg(pl.sum(amount_col).alias(amount_col))
            .sort(category_col, time_frame_col)
            .select(time_frame_col, category_col, amount_col)
        )
        return df

    @staticmethod
    def calculate_income_outcome(
        df: pl.DataFrame,
        source: List[str],
        time_frame_col: str,
        category_col: str,
    ):
        """Calculates the income and outcome balance for a given source over time"""
        distinct_time = df.select(time_frame_col).unique()
        distinct_type = df.select(type_col).unique()
        distinct_time_type = distinct_type.join(distinct_time, how="cross")
        df = df.filter(df[source_col].is_in(source))
        df = df.filter(df[category_col] != "TRANSFERS")  # TODO: MAKE THIS A CONSTANT

        income_outcome = (
            distinct_time_type.join(
                df.group_by(time_frame_col, type_col).agg(
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

    @staticmethod
    def calculate_net_value(df: pl.DataFrame, time_frame_col: str):
        """Calculates the net value for all sources over time."""
        distinct_sources = df.select(source_col).unique()
        distinct_time = df.select(time_frame_col).unique()

        net_value_per_source = (
            distinct_sources.join(distinct_time, how="cross")
            .join(
                df.group_by([source_col, time_frame_col])
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
            net_value_per_source.group_by(time_frame_col)
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

    @staticmethod
    def calculate_goals(
        df: pl.DataFrame, goal_spending: List[Dict[str, int]]
    ) -> pd.DataFrame:
        """
        Calculate and compare actual spending against predefined goals.

        Parameters:
        - df (pl.DataFrame): Input DataFrame with transaction data.
        - goal_spending (List[Dict[str, int]]): List of dictionaries with categories and their respective goal amounts.

        Returns:
        - pd.DataFrame: Pivot table showing whether spending goals were achieved per category each month.
        """
        # Normalize goal spending data
        normalized_data = {
            list(d.keys())[0]: list(d.values())[0] for d in goal_spending
        }
        goals_df = pd.DataFrame(
            normalized_data.items(), columns=["CATEGORY", "MAX_AMOUNT"]
        )

        # Calculate actual spending per category
        actual_spending = CalculateUtils.calculate_transactions_per_category(
            df, "CATEGORY", "YEAR_MONTH"
        ).to_pandas()

        # Determine the date range
        min_date, max_date = (
            actual_spending["YEAR_MONTH"].min(),
            actual_spending["YEAR_MONTH"].max(),
        )

        # Create a complete date range DataFrame
        date_range = (
            pd.date_range(start=min_date, end=max_date, freq="MS")
            .strftime("%Y-%m")
            .tolist()
        )
        date_range_df = pd.DataFrame(date_range, columns=["YEAR_MONTH"])

        # Create all possible combinations of YEAR_MONTH and CATEGORY
        all_combinations = pd.MultiIndex.from_product(
            [date_range_df["YEAR_MONTH"], actual_spending["CATEGORY"].unique()],
            names=["YEAR_MONTH", "CATEGORY"],
        )
        all_combinations_df = pd.DataFrame(index=all_combinations).reset_index()

        # Merge actual spending with all combinations to fill missing months/categories with 0
        actual_spending = pd.merge(
            all_combinations_df,
            actual_spending,
            on=["CATEGORY", "YEAR_MONTH"],
            how="left",
        ).fillna(0)

        # Merge actual spending with goal data
        comparison = pd.merge(actual_spending, goals_df, on="CATEGORY", how="inner")

        # Determine if goals were achieved
        comparison["GOAL_ACHIEVED"] = (
            comparison["MAX_AMOUNT"] > comparison["AMOUNT"].abs()
        )

        # Add a human-readable month column
        comparison["MONTH"] = pd.to_datetime(comparison["YEAR_MONTH"]).dt.strftime(
            "%B %Y"
        )

        # Create a pivot table to summarize goal achievements per month and category
        pivot_table_goals = (
            pd.pivot_table(
                comparison,
                values="GOAL_ACHIEVED",
                index=["MONTH", "YEAR_MONTH"],
                columns="CATEGORY",
                aggfunc="sum",
            )
            .sort_values("YEAR_MONTH")
            .reset_index(level="YEAR_MONTH")
            .drop(columns=["YEAR_MONTH"], axis=1)
            .T
        )

        return pivot_table_goals
