"""
Visualization module for AB testing results.

This module provides functions for creating visualizations of AB test results,
including conversion rates, confidence intervals, and sequential testing results.
"""
from typing import Dict, Tuple, Optional, Union, List, Any
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from .hypothesis_testing import TestResult


def plot_conversion_rates(
    test_result: TestResult,
    title: str = "Conversion Rate Comparison",
    decimal_places: int = 2,
    figsize: Tuple[int, int] = (10, 6)
) -> plt.Figure:
    """Creates a bar chart comparing conversion rates between control and treatment.

    Args:
        test_result: Results of a statistical test
        title: Plot title (default: "Conversion Rate Comparison")
        decimal_places: Number of decimal places to display (default: 2)
        figsize: Figure size (width, height) in inches (default: (10, 6))

    Returns:
        plt.Figure: Matplotlib figure object
    """
    # Set up the figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Data for plotting
    groups = ['Control', 'Treatment']
    values = [test_result.control_metric, test_result.treatment_metric]
    
    # Create the bar plot
    bars = ax.bar(groups, values, color=['#1f77b4', '#ff7f0e'])
    
    # Add a horizontal line for the control rate (for reference)
    ax.axhline(y=test_result.control_metric, color='#1f77b4', linestyle='--', alpha=0.5)
    
    # Add text labels on top of the bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2., 
            height * 1.01,
            f'{values[i]:.{decimal_places}f}', 
            ha='center', 
            va='bottom'
        )
    
    # Add relative lift annotation between the bars
    if test_result.relative_difference != np.inf:
        ax.annotate(
            f"{test_result.relative_difference:+.{decimal_places}f}%",
            xy=(1, max(values) * 0.5),
            xytext=(0.5, max(values) * 0.6),
            arrowprops=dict(arrowstyle="->", color='green' if test_result.relative_difference > 0 else 'red'),
            ha='center'
        )
    
    # Add significance indicator
    significance_text = "Statistically Significant" if test_result.significant else "Not Statistically Significant"
    p_value_text = f"p-value: {test_result.p_value:.{decimal_places}f}"
    ax.annotate(
        f"{significance_text}\n{p_value_text}",
        xy=(0.5, 0),
        xytext=(0.5, -0.15),
        xycoords='axes fraction',
        textcoords='axes fraction',
        ha='center',
        fontweight='bold'
    )
    
    # Set y-axis to start from 0
    ax.set_ylim(bottom=0)
    
    # Add title and labels
    ax.set_title(title)
    ax.set_ylabel('Conversion Rate')
    
    # Tight layout
    fig.tight_layout()
    
    return fig


def plot_confidence_interval(
    test_result: TestResult,
    title: str = "Confidence Interval of Difference",
    decimal_places: int = 2,
    figsize: Tuple[int, int] = (10, 6)
) -> plt.Figure:
    """Creates a visualization of the confidence interval for the difference between groups.

    Args:
        test_result: Results of a statistical test
        title: Plot title (default: "Confidence Interval of Difference")
        decimal_places: Number of decimal places to display (default: 2)
        figsize: Figure size (width, height) in inches (default: (10, 6))

    Returns:
        plt.Figure: Matplotlib figure object
    """
    # Set up the figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Get the confidence interval and difference
    ci_lower, ci_upper = test_result.confidence_interval
    difference = test_result.difference
    
    # Create x range for plotting
    x = np.linspace(min(ci_lower - abs(ci_lower * 0.5), 0), max(ci_upper * 1.5, 0.001), 1000)
    
    # Generate a normal distribution curve centered at the difference
    ci_range = ci_upper - ci_lower
    std_dev = ci_range / (2 * 1.96)  # Approximate standard deviation from CI
    y = stats.norm.pdf(x, difference, std_dev)
    
    # Plot the distribution
    ax.plot(x, y, 'b-')
    ax.fill_between(x, 0, y, alpha=0.2)
    
    # Mark the confidence interval
    ax.axvline(x=ci_lower, color='r', linestyle='--')
    ax.axvline(x=ci_upper, color='r', linestyle='--')
    
    # Mark zero
    ax.axvline(x=0, color='k', linestyle='-', alpha=0.3)
    
    # Mark the difference point
    ax.axvline(x=difference, color='g', linestyle='-')
    ax.plot(difference, 0, 'go', markersize=10)
    
    # Add annotations
    ax.annotate(
        f"Difference: {difference:.{decimal_places}f}",
        xy=(difference, 0),
        xytext=(difference, max(y) * 0.7),
        ha='center',
        arrowprops=dict(arrowstyle="->")
    )
    
    ax.annotate(
        f"CI Lower: {ci_lower:.{decimal_places}f}",
        xy=(ci_lower, 0),
        xytext=(ci_lower, max(y) * 0.5),
        ha='right',
        arrowprops=dict(arrowstyle="->")
    )
    
    ax.annotate(
        f"CI Upper: {ci_upper:.{decimal_places}f}",
        xy=(ci_upper, 0),
        xytext=(ci_upper, max(y) * 0.5),
        ha='left',
        arrowprops=dict(arrowstyle="->")
    )
    
    # Add significance indicator
    contains_zero = (ci_lower <= 0 <= ci_upper)
    if contains_zero:
        interpretation = "Confidence interval contains zero — No significant difference detected"
    else:
        interpretation = "Confidence interval does not contain zero — Significant difference detected"
    
    ax.annotate(
        interpretation,
        xy=(0.5, 0),
        xytext=(0.5, -0.1),
        xycoords='axes fraction',
        textcoords='axes fraction',
        ha='center',
        fontweight='bold'
    )
    
    # Set labels and title
    ax.set_title(title)
    ax.set_xlabel('Difference (Treatment - Control)')
    ax.set_ylabel('Density')
    
    # Remove y-axis ticks for cleaner look
    ax.set_yticks([])
    
    # Tight layout
    fig.tight_layout()
    
    return fig


def plot_daily_metrics(
    daily_data: pd.DataFrame,
    metric_col: str,
    date_col: str,
    group_col: str,
    control_value: Any,
    treatment_value: Any,
    title: str = "Daily Metrics",
    figsize: Tuple[int, int] = (12, 6)
) -> plt.Figure:
    """Creates a line plot showing daily metrics for control and treatment groups.

    Args:
        daily_data: DataFrame containing daily data
        metric_col: Column name for the metric to plot
        date_col: Column name for dates
        group_col: Column name for group assignment
        control_value: Value indicating control group in group_col
        treatment_value: Value indicating treatment group in group_col
        title: Plot title (default: "Daily Metrics")
        figsize: Figure size (width, height) in inches (default: (12, 6))

    Returns:
        plt.Figure: Matplotlib figure object
    """
    # Set up the figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Ensure date is datetime
    if not pd.api.types.is_datetime64_dtype(daily_data[date_col]):
        daily_data = daily_data.copy()
        daily_data[date_col] = pd.to_datetime(daily_data[date_col])
    
    # Extract data for each group
    control_data = daily_data[daily_data[group_col] == control_value]
    treatment_data = daily_data[daily_data[group_col] == treatment_value]
    
    # Calculate overall averages
    control_avg = control_data[metric_col].mean()
    treatment_avg = treatment_data[metric_col].mean()
    
    # Plot the daily values
    ax.plot(control_data[date_col], control_data[metric_col], 'b-', label='Control Daily')
    ax.plot(treatment_data[date_col], treatment_data[metric_col], 'r-', label='Treatment Daily')
    
    # Add horizontal lines for overall averages
    ax.axhline(y=control_avg, color='b', linestyle='--', label=f'Control Avg: {control_avg:.4f}')
    ax.axhline(y=treatment_avg, color='r', linestyle='--', label=f'Treatment Avg: {treatment_avg:.4f}')
    
    # Format x-axis as dates
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    
    # Add labels and title
    ax.set_xlabel('Date')
    ax.set_ylabel(metric_col)
    ax.set_title(title)
    
    # Add legend
    ax.legend()
    
    # Tight layout
    fig.tight_layout()
    
    return fig 