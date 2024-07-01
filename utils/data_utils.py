import streamlit as st
import polars as pl
from utils.constants import source_col, date_col
import pandera as pa
import pandas as pd


def get_all_sources(df):
    """Returns a list of all sources available in the data."""
    return sorted(df.select(source_col).unique().to_series().to_list())


def get_first_last_date(df):
    """Returns the first and last date in the data. Used to set the date picker."""
    first_date = df.select(date_col).min().item()[0:10]
    last_date = df.select(date_col).max().item()[0:10]
    return first_date, last_date


def filter_data(data, start_date, end_date):
    """Filters the data to the selected date range."""
    data = data.filter(
        (pl.col(date_col) >= start_date) & (pl.col(date_col) <= end_date)
    )
    return data


def add_columns(df):
    data = df.with_columns(
        [
            pl.col("DATE").str.strptime(pl.Date, "%Y-%m-%d").alias("DATE"),
        ]
    )
    data = data.with_columns(
        pl.col("DATE").dt.strftime("%Y-%m").alias("YEAR_MONTH"),
        pl.col("DATE").dt.strftime("%YW%V").alias("YEAR_WEEK"),
        pl.when(pl.col("AMOUNT") > 0)
        .then(pl.lit("INCOMING"))
        .otherwise(pl.lit("OUTGOING"))
        .alias("TYPE"),
        pl.col("DATE").cast(pl.String),
    )
    return data


def validate_data(df):
    df = df.to_pandas()

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
