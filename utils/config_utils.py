from typing import Dict, List

import streamlit as st
import yaml
from pydantic import BaseModel, StrictBool, ValidationError


class DashboardConfigData(BaseModel):
    """Pydantic model for dashboard configuration data."""

    display_data: StrictBool
    currency: str
    hidden_categories_from_barplot: List[str]
    pieplot_colors: List[str]
    lineplot_colors: Dict[str, str]
    lineplot_width: Dict[str, int]
    income_category: str
    goals: Dict[str, int]


class MappingConfigData(BaseModel):
    """Pydantic model for mapping configuration data."""

    CATEGORIES: Dict[str, List[str]]
    SUBCATEGORIES: Dict[str, List[str]]


def validate_config_format(config: Dict, config_data_class: BaseModel) -> None:
    """Validate the configuration file format using a Pydantic model."""
    try:
        config_data_class(**config)  # Pass data to the Pydantic model for validation
    except ValidationError as e:
        for error in e.errors():
            st.error(error["loc"][0] + " " + error["msg"])
            st.stop()


def read_config(path: str) -> Dict:
    """Read and parse a YAML configuration file."""
    with open(path) as stream:
        try:
            config = yaml.safe_load(stream)
            return config
        except yaml.YAMLError as exc:
            st.error(exc)
