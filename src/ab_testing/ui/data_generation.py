"""
Data generation UI components for AB Testing application.

This module provides UI components for generating sample data from different distributions
to help users understand AB testing concepts.
"""
from typing import Tuple
import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
from src.ab_testing.stats.generate_samples import generate_normal_samples, generate_binomial_samples


def render_data_generation_section() -> None:
    """
    Render the data generation section of the UI.
    """
    st.header("Generate Sample Data")
    st.markdown("""
    Use this tool to generate sample data from different distributions to understand
    how AB testing works with different types of data.
    """)
    
    # Distribution selection
    dist_type = st.radio(
        "Select Distribution Type",
        ["Normal Distribution", "Binary Distribution (0/1)"],
        horizontal=True
    )
    
    # Sample size input
    sample_size = st.number_input(
        "Sample Size",
        min_value=10,
        max_value=10000,
        value=1000,
        step=100
    )
    
    if dist_type == "Normal Distribution":
        # Parameters for normal distribution
        col1, col2 = st.columns(2)
        with col1:
            mean = st.number_input(
                "Mean",
                value=0.0,
                step=0.1
            )
        with col2:
            std = st.number_input(
                "Standard Deviation",
                min_value=0.1,
                value=1.0,
                step=0.1
            )
        
        # Generate and display data
        if st.button("Generate Normal Samples"):
            samples = generate_normal_samples(mean, std, sample_size)
            display_samples(samples, "Normal Distribution")
    
    else:  # Binary Distribution
        # Parameter for binary distribution
        prob = st.slider(
            "Probability of Success (1)",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.01
        )
        
        # Generate and display data
        if st.button("Generate Binary Samples"):
            samples = generate_binomial_samples(prob, sample_size)
            display_samples(samples, "Binary Distribution")


def display_samples(samples: np.ndarray, dist_name: str) -> None:
    """
    Display generated samples with statistics and visualization.
    
    Args:
        samples: Array of generated samples
        dist_name: Name of the distribution
    """
    # Convert to DataFrame for easier handling
    df = pd.DataFrame(samples, columns=['value'])
    
    # Display statistics
    st.subheader("Sample Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Mean", f"{df['value'].mean():.4f}")
    with col2:
        st.metric("Standard Deviation", f"{df['value'].std():.4f}")
    with col3:
        st.metric("Sample Size", len(df))
    
    # Create and display histogram
    fig = px.histogram(
        df,
        x='value',
        nbins=100,
        title=f"{dist_name} - Sample Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)
