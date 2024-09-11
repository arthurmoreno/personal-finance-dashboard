import streamlit as st


def load_maincss(file_path: str) -> None:
    """Load and apply CSS styles from a file to the Streamlit app."""
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
