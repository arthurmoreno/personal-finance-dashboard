import streamlit as st
import tempfile
import os
from services import ETLProcess

st.title("ETL Process UI")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    if st.button("Run ETL Process"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_input:
            temp_input.write(uploaded_file.read())
            input_path = temp_input.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_output:
            output_path = temp_output.name

        etl = ETLProcess(input_path, output_path)
        etl.run()

        with open(output_path, "rb") as f:
            result_bytes = f.read()

        st.download_button("Download Output CSV", result_bytes, file_name="output.csv", mime="text/csv")

        # Clean up temporary files
        os.remove(input_path)
        os.remove(output_path)
