import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from polars.dataframe import DataFrame
from typing import List
import streamlit_shadcn_ui as ui
import polars as pl
from utils import get_config, AMOUNT_COL, TYPE_COL, SOURCE_COL
import altair as alt

config = get_config()
HIDDEN_CATEGORIES_FROM_BARPLOT = config["hidden_categories_from_barplot"]
PIEPLOT_COLORS = config["pieplot_colors"]
LINEPLOT_COLORS = config["lineplot_colors"]
LINEPLOT_WIDTH = config["lineplot_width"]
CURRENCY = config["currency"]


def plot_net_value_line_plot(df: DataFrame, time_frame_col: str):
    """Plots a line plot of net value for all sources over time."""
    # Assuming df, time_frame_col, and SOURCE_COL are defined
    fig = px.line(df, x=time_frame_col, y="NET_VALUE", color=SOURCE_COL)

    # Update traces with custom colors and line widths
    for trace in fig.data:
        source = trace.name  # Get the name of the source
        trace.update(
            line=dict(
                color=LINEPLOT_COLORS.get(source),
                width=LINEPLOT_WIDTH.get(source),
            )
        )

    # Update layout
    fig.update_layout(yaxis_title="Net value")

    # Plot the figure with Streamlit
    st.plotly_chart(fig, use_container_width=True)


def plot_transactions_per_category(df, category_col, time_frame_col):
    """Plots a bar plot of transactions per category."""
    fig = px.bar(
        df,
        x=time_frame_col,
        y=AMOUNT_COL,
        color=f"{category_col}",
        category_orders={time_frame_col: df[time_frame_col].unique().sort().to_list()},
    )
    fig.update_layout(yaxis_title="Amount")
    fig_go = go.Figure(fig)

    [
        trace.update(visible="legendonly")
        for trace in fig_go.data
        if trace.name in HIDDEN_CATEGORIES_FROM_BARPLOT
    ]

    st.plotly_chart(fig_go, use_container_width=True)


def plot_lineplot_income_outcome(df: DataFrame, time_frame_col: str):
    """Plots a line plot of income, outcome for a given source over time."""
    fig = px.bar(df, x=time_frame_col, y=AMOUNT_COL, color=TYPE_COL, barmode="group")
    fig.update_layout(yaxis_title="Amount")
    st.plotly_chart(fig, use_container_width=True)


def plot_net_value_tiles(df: DataFrame, time_frame_col: str, all_sources: List[str]):
    """Plots tiles of the net value for all sources for the most recent timeframe and a
    ToT (Time over Time) difference with the previous timeframe.
    """

    def create_metric_card(title, content, description):
        ui.metric_card(
            title,
            f"{content:.2f}",
            f"{description:.2f}" + CURRENCY,
        )

    last_period = df.select(pl.col(time_frame_col).max()).item()
    df = df.filter(pl.col(time_frame_col) == last_period)
    n_cols = 3
    cols = st.columns(n_cols)
    for i, source in enumerate(all_sources + ["Total"]):
        source_data = df.filter(pl.col(SOURCE_COL) == source)
        net_value_source = source_data.select("NET_VALUE").item()
        ToT_net_value_source = source_data.select("ToT").item()
        with cols[i % n_cols]:
            create_metric_card(source, net_value_source, ToT_net_value_source)


def plot_pieplot(data):
    operation_select = alt.selection_single(fields=["SUBCATEGORY"], empty="all")

    pie_plot = (
        alt.Chart(data)
        .mark_arc(innerRadius=50)
        .encode(
            theta=alt.Theta(
                "AMOUNT",
                type="quantitative",
                aggregate="sum",
            ),
            color=alt.Color(
                field="SUBCATEGORY",
                type="nominal",
                scale=alt.Scale(
                    domain=data["SUBCATEGORY"].to_list(),
                    range=PIEPLOT_COLORS,
                ),
                title="Income sources",
            ),
            opacity=alt.condition(operation_select, alt.value(1), alt.value(0.50)),
        )
    ).add_selection(operation_select)

    return pie_plot
