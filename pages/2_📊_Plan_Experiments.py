"""
AB Testing Calculator - Plan your experiments
"""
import streamlit as st
from src.ab_testing.ui.data_upload import render_data_upload_section
from src.ab_testing.ui.experiment_setup import render_experiment_setup_section, render_experiment_results
from src.ab_testing.ui.results_display import render_results_section
from src.ab_testing.ui.experiment_duration import render_experiment_duration_section

# Set page config
st.set_page_config(
    page_title="Experiment Planning",
    page_icon="📊",
    layout="wide"
)


# Set title
st.markdown("# Experiment Planning")
st.sidebar.header("Experiment Planning")

st.markdown("""
Before running your A/B test, use this planning tool to calculate the required sample size
and estimate how long your experiment will need to run.
""")


st.header("1. Experiment Setup")
experiment_params = render_experiment_setup_section()
render_experiment_results(experiment_params)

st.header("2. Experiment Duration Calculator")
render_experiment_duration_section()

st.markdown("---")

st.header("3. Data Upload")
pretest_data, test_data = render_data_upload_section()

st.header("4. Test Results")
render_results_section()

# Store data in session state for use in other sections
st.session_state['pretest_data'] = pretest_data
st.session_state['test_data'] = test_data
st.session_state['experiment_params'] = experiment_params
