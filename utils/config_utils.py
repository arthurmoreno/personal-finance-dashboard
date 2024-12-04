"""Utils for all related to the configuration files."""

from typing import Any, Dict, List, Type

import streamlit as st
from pydantic import BaseModel, StrictBool, ValidationError
from ruamel.yaml import YAML

yaml = YAML()


class DashboardConfigData(BaseModel):
    """Pydantic model for dashboard configuration data."""

    display_data: StrictBool
    currency: str
    hidden_categories_from_barplot: List[str]
    pieplot_colors: Dict[str, str]
    lineplot_colors: Dict[str, str]
    lineplot_width: Dict[str, int]
    income_category: str
    goals: Dict[str, int]


class CategorizeMappingConfigData(BaseModel):
    """Pydantic model for mapping configuration data."""

    CATEGORIES: Dict[str, List[str]]
    SUBCATEGORIES: Dict[str, List[str]]


def validate_dashboard_config_format(
    config: Dict[str, Any],
    config_data_class: Type[BaseModel] = DashboardConfigData,
) -> None:
    """Validate the configuration file format using a Pydantic model."""
    try:
        config_data_class(**config)  # Pass data to the Pydantic model for validation

    except ValidationError as e:
        for error in e.errors():
            st.error(error['loc'][0] + ' ' + error['msg'])
            st.stop()


def validate_categorize_mapping_config_format(
    config: Dict[str, Any],
    config_data_class: Type[BaseModel] = CategorizeMappingConfigData,
) -> None:
    """Validate the configuration file format using a Pydantic model."""
    try:
        config_data_class(**config)  # Pass data to the Pydantic model for validation

        # Check if any key contains an empty list as a value
        for key, value in config.items():
            if key == 'SUBCATEGORIES':
                empty_subcategories = [k for k, v in value.items() if len(v) == 0]

                if empty_subcategories != []:
                    st.error(
                        f'Subcateogries {empty_subcategories} do not have any rules.'
                        'Add rules to them or delete the subcategory.',
                    )
                    st.stop()
            if key == 'CATEGORIES':
                empty_categories = [k for k, v in value.items() if len(v) == 0]
                if empty_categories != []:
                    st.error(
                        f'Categories {empty_categories} do not have any subcategories.'
                        'Add subcategoires to them or delete the category.',
                    )
                    st.stop()

    except ValidationError as e:
        for error in e.errors():
            st.error(error['loc'][0] + ' ' + error['msg'])
            st.stop()


def read_config(path: str) -> Dict[str, Any]:
    """Read and parse a YAML configuration file."""
    with open(path) as stream:
        try:
            config = yaml.load(stream)
        except yaml.YAMLError as exc:
            st.error(exc)
    return config
