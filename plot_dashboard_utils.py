from polars.dataframe import DataFrame
import polars as pl
import streamlit as st
from plots import PlotUtils
from calculate_utils import CalculateUtils


class PlotDashboardUtils:
    def __init__(self, config_file):
        self.PlotUtils = PlotUtils(config_file=config_file)
        self.CalculateUtils = CalculateUtils()
        self.income_category = config_file["income_category"]

    def display_net_value(self, df, time_frame_col, all_sources):
        """Displays the net value as a line plot over time and as tiles."""
        net_value = self.CalculateUtils.calculate_net_value(df, time_frame_col)
        a, b = st.columns([6, 4])
        with a:
            self.PlotUtils.plot_net_value_line_plot(net_value, time_frame_col)
        with b:
            self.PlotUtils.plot_net_value_tiles(net_value, time_frame_col, all_sources)

    def display_income_outcome(self, df, source, time_frame_col, category_col):
        """Displays the income and outcome for the selected source over time as a lineplot."""
        income_outcome = self.CalculateUtils.calculate_income_outcome(
            df, source, time_frame_col, category_col
        )
        self.PlotUtils.plot_lineplot_income_outcome(income_outcome, time_frame_col)

    def display_transactions_per_category(self, df, category_col, time_frame_col):
        """Displays the transactions per category over time as a barplot."""
        transactions_per_category = (
            self.CalculateUtils.calculate_transactions_per_category(
                df, category_col, time_frame_col
            )
        )
        self.PlotUtils.plot_transactions_per_category(
            transactions_per_category, category_col, time_frame_col
        )

    def display_pieplot(self, df):
        data = (
            df.filter(pl.col("CATEGORY") == self.income_category)
            .group_by("SUBCATEGORY")
            .agg(pl.sum("AMOUNT").alias("AMOUNT"))
            .sort("SUBCATEGORY")
        )
        pieplot = self.PlotUtils.plot_pieplot(data)
        return pieplot
