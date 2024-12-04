"""Data processing functions."""

import datetime as dt
import re
from io import BytesIO
from typing import Any, Dict

import pandas as pd
import pandera as pa
import polars as pl
import streamlit as st

from utils import date_col


def categorize_data(data: pd.DataFrame, config: Dict[str, Any], first_time: bool = True) -> pd.DataFrame:
    """Categorize transactions by checking if a 'rule' is contained in the description column."""
    if first_time:
        # If it is the first time when you categorize the data, we need to add some columns.
        # The other times (when you make corrections to the categorization afterwards), these
        # columns should already be filled in.
        data = data.assign(SUBCATEGORY='UNKNOWN', CATEGORY='UNKNOWN')
        # These two counts should be at most 1! Otherwise mutliple rules are applied to a transaction
        data = data.assign(SUBCATEGORY_COUNT=0, CATEGORY_COUNT=0)

        # The subcategories should always be defined based on the description
        subcategories = config['SUBCATEGORIES']
        for subcategory, rules in subcategories.items():
            all_rules = '|'.join(re.escape(rule) for rule in rules)

            # find all
            match_with_rule = data['DESCRIPTION'].str.contains(all_rules, na=False)
            data.loc[match_with_rule, 'SUBCATEGORY_COUNT'] += 1
            data.loc[match_with_rule, 'SUBCATEGORY'] = subcategory

    # This is outside the loop because we allow people to change the subcategory
    # after the initial categorization manually, but we force them to have the category
    # belonging to that subcategory
    categories = config['CATEGORIES']
    for category, subcategories in categories.items():
        all_subcategories = '|'.join(subcategory for subcategory in subcategories)
        # find all transactions where the subcategory matches the
        # subcategories of the category
        match_with_subcategory = data['SUBCATEGORY'].str.contains(all_subcategories, na=False)
        if first_time:
            data.loc[match_with_subcategory, 'CATEGORY_COUNT'] += 1
        data.loc[match_with_subcategory, 'CATEGORY'] = category
    return data


def validate_data_after_categorization(data_to_validate: pd.DataFrame) -> None:
    """Validates the processed data.

    To to ensure there are no duplicate categories or subcategories and
    all transactions are categorized correctly.
    """
    data = data_to_validate.copy()

    multiple_subcategories_per_transaction = data[data['SUBCATEGORY_COUNT'] > 1]
    if multiple_subcategories_per_transaction.shape[0] != 0:
        st.error(
            """Some of your transactions have multiple subcategories assigned to them.
            Please ensure that each transaction is assigned to one subcategories only.""",
        )
        st.write(multiple_subcategories_per_transaction[['DATE', 'DESCRIPTION', 'AMOUNT', 'SOURCE']])
        st.stop()

    multiple_categories_per_transaction = data[data['CATEGORY_COUNT'] > 1]
    if multiple_categories_per_transaction.shape[0] != 0:
        st.error(
            """Some of your transactions have multiple categories assigned to them.
            Please ensure that each transaction is assigned to one category only.""",
        )
        st.write(multiple_categories_per_transaction[['DATE', 'DESCRIPTION', 'AMOUNT', 'SOURCE']])
        st.write(multiple_categories_per_transaction)
        st.stop()

    no_category_match = data[data['SUBCATEGORY_COUNT'] > data['CATEGORY_COUNT']]
    if no_category_match.shape[0] != 0:
        st.error(
            """Some of your subcategories have not been assigned to a category in the
            config file.""",
        )
        st.write(no_category_match)
        st.stop()

    unknown_filter = (
        (data['SUBCATEGORY'] == 'UNKNOWN') & (data['SUBCATEGORY_COUNT'] == 0) & (data['CATEGORY_COUNT'] == 0)
    )

    if data[unknown_filter].shape[0] != data[data['SUBCATEGORY'] == 'UNKNOWN'].shape[0]:
        st.error(
            """Your Unknown subcategory seems to have issues. Make sure you do not specify this category
            yourself. This category will be assigned to transactions that do not match with the other categories.""",
        )  # not sure what the point of this is anymore


def get_first_last_date(transactions: pd.DataFrame):
    """Returns the first and last date in the data. Used to set the date picker."""
    # 0:10 to get the string that indicates YYYY-MM-DD
    first_date = transactions.select(date_col).min().item()  # [0:10]
    last_date = transactions.select(date_col).max().item()  # [0:10]
    return first_date, last_date


def filter_data(data: pl.DataFrame, start_date: dt.date, end_date: dt.date):
    """Filters the data to the selected date range."""
    data = data.filter((pl.col(date_col) >= start_date) & (pl.col(date_col) <= end_date))
    return data


def add_columns(transactions_data: pl.DataFrame):
    """Add some columns to help out with the dashboard."""
    if str(transactions_data.get_column('DATE').dtype) == 'String':
        transactions_data = transactions_data.with_columns([
            pl.col('DATE').str.strptime(pl.Date, '%Y-%m-%d').alias('DATE'),
        ])
    transactions_data = transactions_data.with_columns(
        pl.col('DATE').dt.strftime('%Y-%m').alias('YEAR_MONTH'),
        pl.col('DATE').dt.strftime('%YW%V').alias('YEAR_WEEK'),
        pl.when(pl.col('AMOUNT') > 0).then(pl.lit('INCOMING')).otherwise(pl.lit('OUTGOING')).alias('TYPE'),
        pl.col('DATE').cast(pl.String),
    )
    return transactions_data


def validate_transactions_data(data_to_validate: pd.DataFrame) -> None:
    """Validates the transactions data. Checks if the columns are present and if the data is valid."""
    data_to_validate = data_to_validate.copy()
    if 'DATE' not in data_to_validate.columns:
        st.error(f"Column 'DATE' not in dataframe. Columns in dataframe: {list(data_to_validate.columns)}")
        st.stop()

    data_to_validate['DATE'] = pd.to_datetime(data_to_validate['DATE'], errors='coerce')

    if data_to_validate['DATE'].isna().sum() > 0:
        st.error('Please check the DATE column. It contains invalid values.')
        st.stop()

    # Define the schema
    schema = pa.DataFrameSchema({
        'AMOUNT': pa.Column(float, nullable=False),
        'SUBCATEGORY': pa.Column(str, nullable=False),
        'CATEGORY': pa.Column(str, nullable=False),
        'SOURCE': pa.Column(str, nullable=False),
    })

    # Validate the DataFrame
    try:
        schema.validate(data_to_validate)
    except pa.errors.SchemaError as e:
        st.error(e)
        st.stop()


def df_to_excel(df: pd.DataFrame) -> bytes:
    """Write df as excel file."""
    # Function to convert DataFrame to Excel
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data
