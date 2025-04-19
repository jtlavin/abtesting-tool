"""
UI component for experiment duration calculation and visualization.

This module provides functions for rendering the experiment duration section of the AB testing app,
allowing users to calculate and visualize the duration of their experiments under different conditions.
"""
from typing import Dict, Tuple, Optional, Any
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from ..stats.experiment_duration import (
    calculate_experiment_duration,
    generate_duration_vs_traffic_data,
    generate_duration_vs_mde_data,
    plot_duration_vs_traffic,
    plot_duration_vs_mde
)
from ..models.experiment import ExperimentParams


def render_experiment_duration_section() -> None:
    """Renders the experiment duration section of the AB testing app.
    
    This section allows users to:
    1. Calculate the required sample size and experiment duration
    2. Visualize how duration changes with traffic allocation
    3. Visualize how duration changes with minimum detectable effect
    """    
    # Check if experiment parameters are set
    if 'experiment_params' not in st.session_state or not st.session_state['experiment_params']:
        st.warning("Please set up experiment parameters first.")
        return
    
    # Get experiment parameters
    exp_params = st.session_state['experiment_params']
    
    # Create tabs for different duration calculation views
    tabs = st.tabs(["Duration Calculator", "Duration vs. Traffic", "Duration vs. MDE"])
    
    with tabs[0]:
        # Pass the baseline rate from experiment parameters
        render_duration_calculator(exp_params.baseline_rate)
    
    with tabs[1]:
        # Pass the baseline rate from experiment parameters
        render_duration_vs_traffic(exp_params.baseline_rate)
    
    with tabs[2]:
        # Pass the baseline rate from experiment parameters
        render_duration_vs_mde(exp_params.baseline_rate)


def render_duration_calculator(initial_baseline_rate: float = 0.1) -> None:
    """Renders the basic experiment duration calculator.
    
    Args:
        initial_baseline_rate: Initial value for baseline conversion rate
    """
    st.subheader("Experiment Duration Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Basic parameters
        baseline_rate = st.number_input(
            "Baseline Conversion Rate",
            min_value=0.001,
            max_value=0.999,
            value=initial_baseline_rate,
            format="%.4f",
            help="The current conversion rate (control group)"
        )
        
        min_detectable_effect = st.number_input(
            "Minimum Detectable Effect (relative)",
            min_value=0.01,
            max_value=1.0,
            value=0.1,
            format="%.2f",
            help="The minimum relative effect size you want to detect (e.g., 0.1 = 10%)"
        )
        
        daily_traffic = st.number_input(
            "Daily Traffic",
            min_value=1,
            max_value=1000000,
            value=1000,
            help="The total number of users visiting the site per day"
        )
    
    with col2:
        # Advanced parameters
        traffic_allocation = st.slider(
            "Traffic Allocation",
            min_value=0.1,
            max_value=1.0,
            value=1.0,
            step=0.05,
            format="%.2f",
            help="Proportion of traffic allocated to the experiment"
        )
        
        control_ratio = st.slider(
            "Control Ratio",
            min_value=0.1,
            max_value=0.9,
            value=0.5,
            step=0.1,
            format="%.1f",
            help="Proportion of experiment traffic allocated to the control group"
        )
        
        power = st.slider(
            "Statistical Power",
            min_value=0.7,
            max_value=0.95,
            value=0.8,
            step=0.05,
            format="%.2f",
            help="Probability of detecting an effect if it exists"
        )
        
        significance_level = st.select_slider(
            "Significance Level",
            options=[0.01, 0.05, 0.1],
            value=0.05,
            format_func=lambda x: f"{x:.2f}",
            help="Probability of false positive (Type I error)"
        )
        
        hypothesis_type = st.selectbox(
            "Hypothesis Type",
            options=["two-sided", "one-sided"],
            index=0,
            help="'Two-sided' tests for any change, 'one-sided' tests for improvement only"
        )
    
    # Calculate duration when button is clicked
    if st.button("Calculate Experiment Duration"):
        with st.spinner("Calculating experiment duration..."):
            duration_info = calculate_experiment_duration(
                baseline_rate=baseline_rate,
                minimum_detectable_effect=min_detectable_effect,
                daily_traffic=daily_traffic,
                traffic_allocation=traffic_allocation,
                control_ratio=control_ratio,
                power=power,
                significance_level=significance_level,
                hypothesis_type=hypothesis_type
            )
            
            # Display results
            st.subheader("Experiment Duration Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Sample Size",
                    f"{duration_info['total_sample_size']:,}",
                    help="Total number of users needed for the experiment"
                )
            
            with col2:
                st.metric(
                    "Control Sample Size",
                    f"{duration_info['control_sample_size']:,}",
                    help="Number of users in the control group"
                )
            
            with col3:
                st.metric(
                    "Treatment Sample Size",
                    f"{duration_info['treatment_sample_size']:,}",
                    help="Number of users in the treatment group"
                )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Daily Experiment Traffic",
                    f"{duration_info['daily_experiment_traffic']:.0f} users/day",
                    help="Daily traffic allocated to the experiment"
                )
            
            with col2:
                st.metric(
                    "Experiment Duration",
                    f"{duration_info['days_required']:.1f} days",
                    help="Expected duration of the experiment"
                )
            
            # Add some explanation
            st.info(
                f"With a baseline conversion rate of {baseline_rate:.1%} and a minimum detectable effect of "
                f"{min_detectable_effect:.0%}, you'll need approximately {duration_info['days_required']:.1f} days "
                f"to run the experiment."
            )


def render_duration_vs_traffic(initial_baseline_rate: float = 0.1) -> None:
    """Renders the experiment duration vs. traffic allocation visualization.
    
    Args:
        initial_baseline_rate: Initial value for baseline conversion rate
    """
    st.subheader("Experiment Duration vs. Traffic Allocation")
    
    # Parameters
    col1, col2 = st.columns(2)
    
    with col1:
        baseline_rate = st.number_input(
            "Baseline Conversion Rate",
            min_value=0.001,
            max_value=0.999,
            value=initial_baseline_rate,
            format="%.4f",
            key="dur_vs_traffic_baseline",
            help="The current conversion rate (control group)"
        )
        
        min_detectable_effect = st.number_input(
            "Minimum Detectable Effect (relative)",
            min_value=0.01,
            max_value=1.0,
            value=0.1,
            format="%.2f",
            key="dur_vs_traffic_mde",
            help="The minimum relative effect size you want to detect (e.g., 0.1 = 10%)"
        )
    
    with col2:
        daily_traffic = st.number_input(
            "Daily Traffic",
            min_value=1,
            max_value=1000000,
            value=1000,
            key="dur_vs_traffic_daily",
            help="The total number of users visiting the site per day"
        )
        
        power = st.slider(
            "Statistical Power",
            min_value=0.7,
            max_value=0.95,
            value=0.8,
            step=0.05,
            format="%.2f",
            key="dur_vs_traffic_power",
            help="Probability of detecting an effect if it exists"
        )
    
    # Generate and plot data
    if st.button("Generate Traffic Allocation Chart"):
        with st.spinner("Generating chart..."):
            # Generate data
            duration_data = generate_duration_vs_traffic_data(
                baseline_rate=baseline_rate,
                minimum_detectable_effect=min_detectable_effect,
                daily_traffic=daily_traffic,
                power=power
            )
            
            # Plot chart
            fig = plot_duration_vs_traffic(duration_data)
            st.pyplot(fig)
            
            # Optionally display the data as a table
            with st.expander("View data table", expanded=False):
                st.dataframe(duration_data[["traffic_allocation", "days_required"]].rename(
                    columns={"traffic_allocation": "Traffic Allocation (%)", "days_required": "Days Required"}
                ))
            
            # Add explanatory text
            st.markdown("### Interpretation")
            st.markdown(
                "This chart shows how the experiment duration changes with different traffic allocation levels. "
                "As you allocate more traffic to the experiment, the time required to reach statistical significance decreases."
            )
            
            # Save data in session state for reference
            st.session_state["duration_vs_traffic_data"] = duration_data


def render_duration_vs_mde(initial_baseline_rate: float = 0.1) -> None:
    """Renders the experiment duration vs. minimum detectable effect visualization.
    
    Args:
        initial_baseline_rate: Initial value for baseline conversion rate
    """
    st.subheader("Experiment Duration vs. Minimum Detectable Effect")
    
    # Parameters
    col1, col2 = st.columns(2)
    
    with col1:
        baseline_rate = st.number_input(
            "Baseline Conversion Rate",
            min_value=0.001,
            max_value=0.999,
            value=initial_baseline_rate,
            format="%.4f",
            key="dur_vs_mde_baseline",
            help="The current conversion rate (control group)"
        )
        
        daily_traffic = st.number_input(
            "Daily Traffic",
            min_value=1,
            max_value=1000000,
            value=1000,
            key="dur_vs_mde_daily",
            help="The total number of users visiting the site per day"
        )
    
    with col2:
        traffic_allocation = st.slider(
            "Traffic Allocation",
            min_value=0.1,
            max_value=1.0,
            value=1.0,
            step=0.1,
            format="%.1f",
            key="dur_vs_mde_traffic",
            help="Proportion of traffic allocated to the experiment"
        )
        
        power = st.slider(
            "Statistical Power",
            min_value=0.7,
            max_value=0.95,
            value=0.8,
            step=0.05,
            format="%.2f",
            key="dur_vs_mde_power",
            help="Probability of detecting an effect if it exists"
        )
    
    # MDE range
    mde_min = st.number_input("Minimum MDE (%)", min_value=1, max_value=50, value=5) / 100
    mde_max = st.number_input("Maximum MDE (%)", min_value=5, max_value=100, value=30) / 100
    
    # Generate and plot data
    if st.button("Generate MDE Chart"):
        with st.spinner("Generating chart..."):
            # Generate MDE range
            mde_range = np.linspace(mde_min, mde_max, 10)
            
            # Generate data
            duration_data = generate_duration_vs_mde_data(
                baseline_rate=baseline_rate,
                mde_range=mde_range,
                daily_traffic=daily_traffic,
                traffic_allocation=traffic_allocation,
                power=power
            )
            
            # Plot chart
            fig = plot_duration_vs_mde(duration_data)
            st.pyplot(fig)
            
            # Optionally display the data as a table
            with st.expander("View data table", expanded=False):
                st.dataframe(duration_data[["minimum_detectable_effect", "days_required"]].rename(
                    columns={"minimum_detectable_effect": "Minimum Detectable Effect (%)", "days_required": "Days Required"}
                ))
            
            # Add explanatory text
            st.markdown("### Interpretation")
            st.markdown(
                "This chart shows how the experiment duration changes with different minimum detectable effect sizes. "
                "The smaller the effect you want to detect, the longer the experiment will take."
            )
            
            # Save data in session state for reference
            st.session_state["duration_vs_mde_data"] = duration_data 