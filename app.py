"""
AB Testing Calculator - Main Application

A Streamlit application for conducting and analyzing AB tests.
"""
import streamlit as st
from src.ab_testing.ui.data_upload import render_data_upload_section
from src.ab_testing.ui.experiment_setup import render_experiment_setup_section


def main() -> None:
    """Main application entry point."""
    # Set page config
    st.set_page_config(
        page_title="AB Testing Calculator",
        page_icon="📊",
        layout="wide"
    )
    
    # Set title
    st.title("AB Testing Calculator")
    
    # Section 1: Data Upload
    pretest_data, test_data = render_data_upload_section()
    
    # Section 2: Experiment Setup
    experiment_params = render_experiment_setup_section()
    
    # Store data in session state for use in other sections
    st.session_state['pretest_data'] = pretest_data
    st.session_state['test_data'] = test_data
    st.session_state['experiment_params'] = experiment_params


if __name__ == "__main__":
    main() 