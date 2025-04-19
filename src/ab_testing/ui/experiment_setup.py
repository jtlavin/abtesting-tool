"""
Experiment setup UI components for AB Testing application.

This module provides UI components for configuring experiment parameters.
"""
from typing import Optional
import streamlit as st
from src.ab_testing.models.experiment import ExperimentParams


def render_experiment_setup_section() -> ExperimentParams:
    """
    Render the experiment setup section of the UI.
    
    Returns:
        ExperimentParams object with user-configured values
    """
    st.header("2. Experiment Setup")
    
    # Create three columns for experiment parameters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        alpha = st.number_input(
            "Significance Level (α)",
            min_value=0.01,
            max_value=0.10,
            value=0.05,
            step=0.01,
            help="Probability of Type I error (false positive)"
        )
    
    with col2:
        power = st.number_input(
            "Statistical Power (1-β)",
            min_value=0.50,
            max_value=0.99,
            value=0.80,
            step=0.01,
            help="Probability of correctly rejecting the null hypothesis"
        )
    
    with col3:
        mde = st.number_input(
            "Minimum Detectable Effect (MDE)",
            min_value=0.01,
            max_value=1.00,
            value=0.10,
            step=0.01,
            help="Minimum effect size you want to detect"
        )
    
    # Baseline conversion rate
    baseline_rate = st.number_input(
        "Baseline Conversion Rate",
        min_value=0.01,
        max_value=1.00,
        value=0.10,
        step=0.01,
        help="Current conversion rate (control group)"
    )
    
    # Create experiment parameters object
    params = ExperimentParams(
        alpha=alpha,
        power=power,
        mde=mde,
        baseline_rate=baseline_rate
    )
    
    # Display hypothesis
    st.subheader("Hypothesis")
    st.write("**Null Hypothesis (Ho):** The conversion rates of control and treatment groups are the same")
    st.write("**Alternative Hypothesis (Ha):** The conversion rates of control and treatment groups are different")
    
    # Validate parameters
    errors = params.validate()
    if errors:
        for param, error in errors.items():
            st.error(f"{param}: {error}")
    
    # Display expected treatment rate
    st.info(f"Expected treatment conversion rate: {params.treatment_rate():.2%} (a {mde*100:.1f}% increase)")
    
    # Add some spacing
    st.write("")
    st.write("")
    
    return params 