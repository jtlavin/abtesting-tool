"""
Experiment duration module for AB testing.

This module provides functions for calculating and visualizing the duration
required for an AB test based on various parameters including baseline conversion rate,
minimum detectable effect, traffic allocation, and statistical power.
"""
from typing import Dict, Tuple, Optional, Union, List, Any
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats


def calculate_sample_size(
    baseline_rate: float,
    minimum_detectable_effect: float,
    power: float = 0.8,
    significance_level: float = 0.05,
    hypothesis_type: str = "two-sided"
) -> int:
    """Calculates the required sample size per variant for an AB test.

    Args:
        baseline_rate: The baseline conversion rate (control group)
        minimum_detectable_effect: The minimum relative effect size to detect (as a decimal)
        power: Statistical power (default: 0.8)
        significance_level: Statistical significance level (default: 0.05)
        hypothesis_type: Type of hypothesis test, 'one-sided' or 'two-sided' (default: 'two-sided')

    Returns:
        int: The required sample size per variant
    """
    # Calculate the absolute effect size
    absolute_effect = baseline_rate * minimum_detectable_effect
    
    # Expected conversion rate for treatment group
    treatment_rate = baseline_rate + absolute_effect
    
    # Standard normal quantiles for significance level and power
    if hypothesis_type == "two-sided":
        z_alpha = stats.norm.ppf(1 - significance_level / 2)
    else:  # one-sided
        z_alpha = stats.norm.ppf(1 - significance_level)
    
    z_beta = stats.norm.ppf(power)
    
    # Standard error under H0 and H1
    se0 = np.sqrt(2 * baseline_rate * (1 - baseline_rate))
    se1 = np.sqrt(baseline_rate * (1 - baseline_rate) + treatment_rate * (1 - treatment_rate))
    
    # Calculate sample size per group
    sample_size = ((z_alpha * se0 + z_beta * se1) / absolute_effect) ** 2
    
    # Round up to the nearest integer
    return int(np.ceil(sample_size))


def calculate_experiment_duration(
    baseline_rate: float,
    minimum_detectable_effect: float,
    daily_traffic: int,
    traffic_allocation: float = 1.0,
    control_ratio: float = 0.5,
    power: float = 0.8,
    significance_level: float = 0.05,
    hypothesis_type: str = "two-sided"
) -> Dict[str, Any]:
    """Calculates the expected duration of an AB test.

    Args:
        baseline_rate: The baseline conversion rate (control group)
        minimum_detectable_effect: The minimum relative effect size to detect (as a decimal)
        daily_traffic: Total number of users visiting the site per day
        traffic_allocation: Proportion of traffic allocated to the experiment (default: 1.0)
        control_ratio: Proportion of experiment traffic allocated to control (default: 0.5)
        power: Statistical power (default: 0.8)
        significance_level: Statistical significance level (default: 0.05)
        hypothesis_type: Type of hypothesis test, 'one-sided' or 'two-sided' (default: 'two-sided')

    Returns:
        Dict[str, Any]: Dictionary containing experiment duration information
    """
    # Calculate required sample size per variant
    sample_size_per_variant = calculate_sample_size(
        baseline_rate=baseline_rate,
        minimum_detectable_effect=minimum_detectable_effect,
        power=power,
        significance_level=significance_level,
        hypothesis_type=hypothesis_type
    )
    
    # Calculate total sample size needed for both variants
    # Adjust for unequal allocation if necessary
    if control_ratio == 0.5:
        total_sample_size = sample_size_per_variant * 2
    else:
        # For unbalanced allocation, we need to adjust the sample size
        # The formula is: n = n_equal * (1 + ratio)^2 / (4 * ratio)
        # Where n_equal is the sample size for balanced allocation
        # and ratio is the proportion between the two groups (smaller/larger)
        ratio = min(control_ratio, 1 - control_ratio) / max(control_ratio, 1 - control_ratio)
        adjustment_factor = (1 + ratio)**2 / (4 * ratio)
        total_sample_size = int(np.ceil(sample_size_per_variant * 2 * adjustment_factor))
    
    # Calculate daily experiment traffic
    daily_experiment_traffic = daily_traffic * traffic_allocation
    
    # Calculate days required
    if daily_experiment_traffic > 0:
        days_required = total_sample_size / daily_experiment_traffic
    else:
        days_required = float('inf')
    
    # Calculate samples per variant
    control_sample = total_sample_size * control_ratio
    treatment_sample = total_sample_size * (1 - control_ratio)
    
    return {
        "total_sample_size": total_sample_size,
        "control_sample_size": int(np.ceil(control_sample)),
        "treatment_sample_size": int(np.ceil(treatment_sample)),
        "days_required": days_required,
        "daily_experiment_traffic": daily_experiment_traffic
    }


def generate_duration_vs_traffic_data(
    baseline_rate: float,
    minimum_detectable_effect: float,
    daily_traffic: int,
    traffic_allocation_range: List[float] = None,
    control_ratio: float = 0.5,
    power: float = 0.8,
    significance_level: float = 0.05,
    hypothesis_type: str = "two-sided"
) -> pd.DataFrame:
    """Generates data for duration vs. traffic allocation chart.

    Args:
        baseline_rate: The baseline conversion rate (control group)
        minimum_detectable_effect: The minimum relative effect size to detect (as a decimal)
        daily_traffic: Total number of users visiting the site per day
        traffic_allocation_range: List of traffic allocation values to simulate (default: None, uses 0.1 to 1.0)
        control_ratio: Proportion of experiment traffic allocated to control (default: 0.5)
        power: Statistical power (default: 0.8)
        significance_level: Statistical significance level (default: 0.05)
        hypothesis_type: Type of hypothesis test, 'one-sided' or 'two-sided' (default: 'two-sided')

    Returns:
        pd.DataFrame: DataFrame containing traffic allocation and corresponding duration
    """
    if traffic_allocation_range is None:
        traffic_allocation_range = np.arange(0.1, 1.05, 0.05)
    
    data = []
    
    for traffic_alloc in traffic_allocation_range:
        duration_info = calculate_experiment_duration(
            baseline_rate=baseline_rate,
            minimum_detectable_effect=minimum_detectable_effect,
            daily_traffic=daily_traffic,
            traffic_allocation=traffic_alloc,
            control_ratio=control_ratio,
            power=power,
            significance_level=significance_level,
            hypothesis_type=hypothesis_type
        )
        
        data.append({
            "traffic_allocation": traffic_alloc * 100,  # Convert to percentage
            "days_required": duration_info["days_required"],
            "daily_experiment_traffic": duration_info["daily_experiment_traffic"],
            "total_sample_size": duration_info["total_sample_size"]
        })
    
    return pd.DataFrame(data)


def generate_duration_vs_mde_data(
    baseline_rate: float,
    mde_range: List[float],
    daily_traffic: int,
    traffic_allocation: float = 1.0,
    control_ratio: float = 0.5,
    power: float = 0.8,
    significance_level: float = 0.05,
    hypothesis_type: str = "two-sided"
) -> pd.DataFrame:
    """Generates data for duration vs. minimum detectable effect chart.

    Args:
        baseline_rate: The baseline conversion rate (control group)
        mde_range: List of minimum detectable effect values to simulate
        daily_traffic: Total number of users visiting the site per day
        traffic_allocation: Proportion of traffic allocated to the experiment (default: 1.0)
        control_ratio: Proportion of experiment traffic allocated to control (default: 0.5)
        power: Statistical power (default: 0.8)
        significance_level: Statistical significance level (default: 0.05)
        hypothesis_type: Type of hypothesis test, 'one-sided' or 'two-sided' (default: 'two-sided')

    Returns:
        pd.DataFrame: DataFrame containing MDE values and corresponding duration
    """
    data = []
    
    for mde in mde_range:
        duration_info = calculate_experiment_duration(
            baseline_rate=baseline_rate,
            minimum_detectable_effect=mde,
            daily_traffic=daily_traffic,
            traffic_allocation=traffic_allocation,
            control_ratio=control_ratio,
            power=power,
            significance_level=significance_level,
            hypothesis_type=hypothesis_type
        )
        
        data.append({
            "minimum_detectable_effect": mde * 100,  # Convert to percentage
            "days_required": duration_info["days_required"],
            "total_sample_size": duration_info["total_sample_size"]
        })
    
    return pd.DataFrame(data)


def plot_duration_vs_traffic(
    df: pd.DataFrame,
    figsize: Tuple[int, int] = (10, 6)
) -> plt.Figure:
    """Creates a plot of experiment duration vs. traffic allocation.

    Args:
        df: DataFrame containing 'traffic_allocation' and 'days_required' columns
        figsize: Figure size (width, height) in inches (default: (10, 6))

    Returns:
        plt.Figure: Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot the data
    ax.plot(df["traffic_allocation"], df["days_required"], 'b-o', linewidth=2)
    
    # Set labels and title
    ax.set_xlabel("Traffic Allocation (%)")
    ax.set_ylabel("Duration (Days)")
    ax.set_title("Experiment Duration vs. Traffic Allocation")
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Annotate a few key points
    n_points = len(df)
    for i in [0, n_points // 2, n_points - 1]:
        x = df.iloc[i]["traffic_allocation"]
        y = df.iloc[i]["days_required"]
        ax.annotate(
            f"{y:.1f} days",
            xy=(x, y),
            xytext=(5, 5),
            textcoords="offset points",
            ha="left"
        )
    
    # Tight layout
    fig.tight_layout()
    
    return fig


def plot_duration_vs_mde(
    df: pd.DataFrame,
    figsize: Tuple[int, int] = (10, 6)
) -> plt.Figure:
    """Creates a plot of experiment duration vs. minimum detectable effect.

    Args:
        df: DataFrame containing 'minimum_detectable_effect' and 'days_required' columns
        figsize: Figure size (width, height) in inches (default: (10, 6))

    Returns:
        plt.Figure: Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot the data
    ax.plot(df["minimum_detectable_effect"], df["days_required"], 'r-o', linewidth=2)
    
    # Set labels and title
    ax.set_xlabel("Minimum Detectable Effect (%)")
    ax.set_ylabel("Duration (Days)")
    ax.set_title("Experiment Duration vs. Minimum Detectable Effect")
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Annotate a few key points
    n_points = len(df)
    for i in [0, n_points // 2, n_points - 1]:
        x = df.iloc[i]["minimum_detectable_effect"]
        y = df.iloc[i]["days_required"]
        ax.annotate(
            f"{y:.1f} days",
            xy=(x, y),
            xytext=(5, 5),
            textcoords="offset points",
            ha="left"
        )
    
    # Tight layout
    fig.tight_layout()
    
    return fig 