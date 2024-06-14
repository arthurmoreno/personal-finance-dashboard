import streamlit_shadcn_ui as ui


def date_picker(key, mode, label, default_value):
    """Displays the date picker and returns the selected dates."""
    return ui.date_picker(key=key, mode=mode, label=label, default_value=default_value)


def create_tabs(mapping):
    # Key is arbitrary here.
    selected = ui.tabs(
        options=mapping.keys(),
        default_value=list(mapping.keys())[0],
        key=list(mapping.keys())[0],
    )
    selected_col = mapping.get(selected)

    return selected_col
