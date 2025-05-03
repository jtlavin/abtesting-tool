"""
AB Testing Calculator - Main Entrypoint
"""
import streamlit as st
# Set page config
st.set_page_config(
    page_title="AB Testing Home",
    page_icon="📊",
    layout="wide"
)
st.write("# AB Testing Home")

st.sidebar.success("Select a page above.")

st.markdown(
    """
    AB Testing Calculator is a tool that helps you plan, execute, and analyze AB tests.
    Based on a course from [Data Interview](https://www.datainterview.com/).
"""
)