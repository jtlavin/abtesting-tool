"""
AB Testing Calculator - Main Application

A Streamlit application for conducting and analyzing AB tests.
"""
import streamlit as st
from src.ab_testing.ui.data_upload import render_data_upload_section
from src.ab_testing.ui.experiment_setup import render_experiment_setup_section
from src.ab_testing.ui.results_display import render_results_section
from src.ab_testing.ui.experiment_duration import render_experiment_duration_section


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
    
    # Section 1: Experiment Duration Calculator
    st.header("1. Experiment Planning")
    st.markdown("""
    Before running your A/B test, use this planning tool to calculate the required sample size
    and estimate how long your experiment will need to run.
    """)
    render_experiment_duration_section()
    
    st.markdown("---")
    
    # Section 2: Data Upload
    st.header("2. Data Upload")
    pretest_data, test_data = render_data_upload_section()
    
    # Section 3: Experiment Setup
    st.header("3. Experiment Setup")
    experiment_params = render_experiment_setup_section()
    
    # Section 4: Test Results
    st.header("4. Test Results")
    render_results_section()
    
    # Store data in session state for use in other sections
    st.session_state['pretest_data'] = pretest_data
    st.session_state['test_data'] = test_data
    st.session_state['experiment_params'] = experiment_params


if __name__ == "__main__":
    main() 