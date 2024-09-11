import re
from io import BytesIO
from typing import Dict

import pandas as pd
import pandera as pa
import polars as pl
import streamlit as st

from utils import date_col, source_col


class TransactionProcessor:
    def __init__(self, config: Dict):
        """Initialize the TransactionProcessor."""
        self.config = config

    def map_categories(
        self, data: pd.DataFrame, first_time: bool = True
    ) -> pd.DataFrame:
        """Maps transaction descriptions to predefined categories and
        subcategories based on matching rules from the YAML file."""
        if first_time:
            data = data.assign(
                SUBCATEGORY="UNKNOWN",
                CATEGORY="UNKNOWN",
            )
            data = data.assign(
                SUBCATEGORY_COUNT=0,
                CATEGORY_COUNT=0,
            )

        subcategories = self.config["SUBCATEGORIES"]
        for (
            subcategory,
            matches,
        ) in subcategories.items():  # TODO: what if string contains "|"
            pattern = "|".join(re.escape(match) for match in matches)

            cond = data["DESCRIPTION"].str.contains(pattern, na=False)
            if first_time:
                data.loc[
                    cond,
                    "SUBCATEGORY_COUNT",
                ] += 1
            data.loc[
                cond,
                "SUBCATEGORY",
            ] = subcategory

        categories = self.config["CATEGORIES"]
        for category, matches in categories.items():
            cond = data["SUBCATEGORY"].apply(lambda x, matches=matches: x in matches)
            if first_time:
                data.loc[
                    cond,
                    "CATEGORY_COUNT",
                ] += 1
            data.loc[
                cond,
                "CATEGORY",
            ] = category
        return data

    def validate_data(self, data_to_validate):
        data = data_to_validate.copy()
        """Validates the processed data to ensure there are no duplicate categories
        or subcategories and all transactions are categorized correctly."""

        multiple_subcategories_per_transaction = data[data["SUBCATEGORY_COUNT"] > 1]
        if multiple_subcategories_per_transaction.shape[0] != 0:
            st.error(
                """Some of your transactions have multiple subcategories assigned to them.
                Please ensure that each transaction is assigned to one subcategories only."""
            )
            st.write(
                multiple_subcategories_per_transaction[
                    ["DATE", "DESCRIPTION", "AMOUNT", "SOURCE"]
                ]
            )
            st.stop()

        multiple_categories_per_transaction = data[data["CATEGORY_COUNT"] > 1]
        if multiple_categories_per_transaction.shape[0] != 0:
            st.error(
                """Some of your transactions have multiple categories assigned to them.
                Please ensure that each transaction is assigned to one category only."""
            )
            st.write(
                multiple_categories_per_transaction[
                    ["DATE", "DESCRIPTION", "AMOUNT", "SOURCE"]
                ]
            )
            st.stop()

        no_category_match = data[data["SUBCATEGORY_COUNT"] > data["CATEGORY_COUNT"]]
        if no_category_match.shape[0] != 0:
            st.error(
                """Some of your subcategories have not been assigned to a category in the
                config file."""
            )
            st.write(no_category_match)
            st.stop()

        unknown_filter = (
            (data["SUBCATEGORY"] == "UNKNOWN")
            & (data["SUBCATEGORY_COUNT"] == 0)
            & (data["CATEGORY_COUNT"] == 0)
        )

        if (
            data[unknown_filter].shape[0]
            != data[data["SUBCATEGORY"] == "UNKNOWN"].shape[0]
        ):
            st.error(
                """Your Unknown subcategory seems to have issues. Make sure you do not specify this category
                yourself. This category will be assigned to transactions that do not match with the other categories."""
            )  # not sure what the point of this is anymore

    def remove_columns(self, data):
        """Removes columns that are not needed for the analysis."""
        return data.drop(["SUBCATEGORY_COUNT", "CATEGORY_COUNT"], axis=1)

    def write_data(self, data, filename):
        """Writes the processed transaction data to an Excel file with the specified filename."""
        data = data.select(self.select_columns)
        data.to_excel(filename, index=False)

    def map_and_validate_categories(self, org_data):
        categorized_data = self.map_categories(org_data)
        self.validate_data(categorized_data)
        categorized_data = self.remove_columns(categorized_data)
        return categorized_data


def get_all_sources(df):
    """Returns a list of all sources available in the data."""
    return sorted(df.select(source_col).unique().to_series().to_list())


def get_first_last_date(df):
    """Returns the first and last date in the data. Used to set the date picker."""
    # 0:10 to get the string that indicates YYYY-MM-DD
    first_date = df.select(date_col).min().item()  # [0:10]
    last_date = df.select(date_col).max().item()  # [0:10]
    return first_date, last_date


def filter_data(data, start_date, end_date):
    """Filters the data to the selected date range."""
    data = data.filter(
        (pl.col(date_col) >= start_date) & (pl.col(date_col) <= end_date)
    )
    return data


def add_columns(df):
    if str(df.get_column("DATE").dtype) == "String":
        df = df.with_columns(
            [
                pl.col("DATE").str.strptime(pl.Date, "%Y-%m-%d").alias("DATE"),
            ]
        )
    data = df.with_columns(
        pl.col("DATE").dt.strftime("%Y-%m").alias("YEAR_MONTH"),
        pl.col("DATE").dt.strftime("%YW%V").alias("YEAR_WEEK"),
        pl.when(pl.col("AMOUNT") > 0)
        .then(pl.lit("INCOMING"))
        .otherwise(pl.lit("OUTGOING"))
        .alias("TYPE"),
        pl.col("DATE").cast(pl.String),
    )
    return data


def validate_data(data_to_validate):
    df = data_to_validate.copy()
    if "DATE" not in df.columns:
        st.error(
            f"Column 'DATE' not in dataframe. Columns in dataframe: {list(df.columns)}"
        )
        st.stop()

    df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")

    if df["DATE"].isna().sum() > 0:
        st.error("Please check the DATE column. It contains invalid values.")
        st.stop()

    # Define the schema
    schema = pa.DataFrameSchema(
        {
            "AMOUNT": pa.Column(float, nullable=False),
            "SUBCATEGORY": pa.Column(str, nullable=False),
            "CATEGORY": pa.Column(str, nullable=False),
            "SOURCE": pa.Column(str, nullable=False),
        }
    )

    # Validate the DataFrame
    try:
        schema.validate(df)
    except pa.errors.SchemaError as e:
        st.error(e)
        st.stop()


def df_to_excel(df):
    # Function to convert DataFrame to Excel
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, index=False, sheet_name="Sheet1")
    writer.close()
    processed_data = output.getvalue()
    return processed_data
