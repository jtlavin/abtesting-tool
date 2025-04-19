"""
UI component for displaying AB test results.

This module provides functions for rendering the results of AB tests in a Streamlit app,
including statistical analysis, visualizations, and interpretations.
"""
from typing import Dict, Tuple, Optional, Any
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from ..stats.hypothesis_testing import proportion_test, mean_test, TestResult
from ..stats.validation import aa_test, sample_ratio_mismatch
from ..stats.visualization import (
    plot_conversion_rates, 
    plot_confidence_interval,
    plot_daily_metrics
)
from ..models.experiment import ExperimentParams


def render_results_section() -> None:
    """Renders the results section of the AB testing app.
    
    This section displays:
    1. Statistical results of the AB test
    2. Visualizations of the results
    3. Validation checks
    4. Interpretation and recommendations
    """
    
    # Check if data is available
    if 'test_data' not in st.session_state or st.session_state['test_data'] is None:
        st.warning("Please upload test data first.")
        return
    
    # Check if experiment parameters are set
    if 'experiment_params' not in st.session_state or not st.session_state['experiment_params']:
        st.warning("Please set up experiment parameters first.")
        return
    
    # Get the data and parameters
    test_data = st.session_state['test_data']
    pretest_data = st.session_state.get('pretest_data')
    exp_params = st.session_state['experiment_params']
    
    # Define default column names
    group_col = 'group'
    conversion_col = 'submitted'
    date_col = 'date'
    
    # Default group values
    control_value = 0
    treatment_value = 1
    
    # Extract control and treatment groups
    try:
        control_group = test_data[test_data[group_col] == control_value][conversion_col]
        treatment_group = test_data[test_data[group_col] == treatment_value][conversion_col]
        
        # Check if groups are not empty
        if len(control_group) == 0 or len(treatment_group) == 0:
            st.error(f"One or both groups are empty. Please check your data and group values.")
            return
    except KeyError as e:
        st.error(f"Column not found in data: {e}")
        return
    
    # Create tabs for different sections
    tabs = st.tabs(["Statistical Analysis", "Visualizations", "Validation Checks", "Interpretation"])
    
    with tabs[0]:  # Statistical Analysis
        render_statistical_analysis(control_group, treatment_group, exp_params)
    
    with tabs[1]:  # Visualizations
        render_visualizations(test_data, control_group, treatment_group, group_col, conversion_col, date_col, control_value, treatment_value)
    
    with tabs[2]:  # Validation Checks
        render_validation_checks(pretest_data, test_data, group_col, conversion_col, control_value, treatment_value)
    
    with tabs[3]:  # Interpretation
        render_interpretation()


def render_statistical_analysis(
    control_group: pd.Series,
    treatment_group: pd.Series,
    exp_params: ExperimentParams
) -> None:
    """Renders the statistical analysis section.
    
    Args:
        control_group: Data from the control group
        treatment_group: Data from the treatment group
        exp_params: Experiment parameters
    """
    st.subheader("Statistical Analysis")
    
    # Compute basic statistics
    control_size = len(control_group)
    treatment_size = len(treatment_group)
    control_successes = control_group.sum()
    treatment_successes = treatment_group.sum()
    control_rate = control_successes / control_size
    treatment_rate = treatment_successes / treatment_size
    
    # Display basic statistics in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Control Group Size", control_size)
        st.metric("Control Successes", control_successes)
        st.metric("Control Rate", f"{control_rate:.4f}")
    
    with col2:
        st.metric("Treatment Group Size", treatment_size)
        st.metric("Treatment Successes", treatment_successes)
        st.metric("Treatment Rate", f"{treatment_rate:.4f}")
    
    # Selection for test type and confidence level
    test_type = st.selectbox(
        "Test Type", 
        ["Proportion Test (Binary Metric)"],
        help="Select the type of statistical test to perform"
    )
    
    confidence_level = st.slider(
        "Confidence Level", 
        min_value=0.8, 
        max_value=0.99, 
        value=0.95, 
        step=0.01,
        help="Select the confidence level for the statistical test"
    )
    
    alternative = st.selectbox(
        "Alternative Hypothesis",
        ["two-sided", "larger", "smaller"],
        help="Select the alternative hypothesis: two-sided (treatment ≠ control), larger (treatment > control), or smaller (treatment < control)"
    )
    
    # Perform statistical test
    if st.button("Run Statistical Test"):
        with st.spinner("Performing statistical test..."):
            if test_type == "Proportion Test (Binary Metric)":
                result = proportion_test(
                    control_successes=int(control_successes),
                    control_size=control_size,
                    treatment_successes=int(treatment_successes),
                    treatment_size=treatment_size,
                    confidence_level=confidence_level,
                    alternative=alternative
                )
                
                display_test_results(result)
                
                # Store the result for use in other tabs
                st.session_state['test_result'] = result


def display_test_results(result: TestResult) -> None:
    """Displays the results of a statistical test.
    
    Args:
        result: Results of the statistical test
    """
    # Create an expander for detailed results
    with st.expander("Detailed Test Results", expanded=True):
        st.write(f"**Test Method:** {result.method}")
        st.write(f"**p-value:** {result.p_value:.6f}")
        st.write(f"**Test Statistic:** {result.statistic:.4f}")
        
        # Show confidence interval
        ci_lower, ci_upper = result.confidence_interval
        st.write(f"**Confidence Interval:** [{ci_lower:.6f}, {ci_upper:.6f}]")
        
        # Show absolute and relative differences
        st.write(f"**Absolute Difference:** {result.difference:.6f}")
        rel_diff = result.relative_difference
        
        if rel_diff != np.inf:
            st.write(f"**Relative Difference:** {rel_diff:.2f}%")
        
        # Significance assessment
        if result.significant:
            st.success("The difference is statistically significant.")
        else:
            st.info("The difference is not statistically significant.")
        
        # Additional interpretation of confidence interval
        contains_zero = (ci_lower <= 0 <= ci_upper)
        if contains_zero:
            st.info("The confidence interval contains zero, suggesting no significant effect.")
        else:
            if ci_lower > 0:
                st.success("The confidence interval is entirely positive, suggesting a positive effect.")
            else:
                st.warning("The confidence interval is entirely negative, suggesting a negative effect.")


def render_visualizations(
    test_data: pd.DataFrame,
    control_group: pd.Series,
    treatment_group: pd.Series,
    group_col: str,
    conversion_col: str,
    date_col: str,
    control_value: Any,
    treatment_value: Any
) -> None:
    """Renders visualizations of AB test results.
    
    Args:
        test_data: The full test dataset
        control_group: Data from the control group
        treatment_group: Data from the treatment group
        group_col: Name of the column containing group assignment
        conversion_col: Name of the column containing conversion data
        date_col: Name of the column containing dates
        control_value: Value identifying the control group
        treatment_value: Value identifying the treatment group
    """
    st.subheader("Visualizations")
    
    # Check if we have test results
    if 'test_result' not in st.session_state:
        st.warning("Run the statistical test first to generate visualizations.")
        return
    
    result = st.session_state['test_result']
    
    # Create conversion rate comparison chart
    st.subheader("Conversion Rate Comparison")
    fig_rates = plot_conversion_rates(
        result, 
        title="Conversion Rate Comparison",
        decimal_places=4
    )
    st.pyplot(fig_rates)
    
    # Create confidence interval visualization
    st.subheader("Confidence Interval Visualization")
    fig_ci = plot_confidence_interval(
        result,
        title="95% Confidence Interval for Difference",
        decimal_places=4
    )
    st.pyplot(fig_ci)
    
    # If we have daily data, show trends over time
    if date_col in test_data.columns:
        st.subheader("Daily Conversion Rates")
        
        try:
            # Calculate daily conversion rates
            daily_data = test_data.groupby([group_col, date_col])[conversion_col].mean().reset_index()
            
            fig_daily = plot_daily_metrics(
                daily_data=daily_data,
                metric_col=conversion_col,
                date_col=date_col,
                group_col=group_col,
                control_value=control_value,
                treatment_value=treatment_value,
                title="Daily Conversion Rates"
            )
            st.pyplot(fig_daily)
        except Exception as e:
            st.error(f"Could not generate daily metrics chart: {e}")


def render_validation_checks(
    pretest_data: Optional[pd.DataFrame],
    test_data: pd.DataFrame,
    group_col: str,
    conversion_col: str,
    control_value: Any,
    treatment_value: Any
) -> None:
    """Renders validation checks for the AB test.
    
    Args:
        pretest_data: Pre-test data for AA test validation (if available)
        test_data: The test dataset
        group_col: Name of the column containing group assignment
        conversion_col: Name of the column containing conversion data
        control_value: Value identifying the control group
        treatment_value: Value identifying the treatment group
    """
    st.subheader("Validation Checks")
    
    # Sample Ratio Mismatch (SRM) Check
    st.write("#### Sample Ratio Mismatch (SRM) Check")
    
    try:
        # Calculate group sizes
        control_size = len(test_data[test_data[group_col] == control_value])
        treatment_size = len(test_data[test_data[group_col] == treatment_value])
        
        # Expected ratio (default is 50/50)
        expected_ratio = 0.5
        
        # Perform SRM check
        srm_result = sample_ratio_mismatch(
            control_size=control_size,
            treatment_size=treatment_size,
            expected_ratio=expected_ratio
        )
        
        # Display results
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Control Size", control_size)
            st.metric("Treatment Size", treatment_size)
        
        with col2:
            st.metric("Expected Ratio", f"{expected_ratio:.2f}")
            st.metric("p-value", f"{srm_result.p_value:.4f}")
        
        # Display pass/fail message
        if srm_result.passed:
            st.success("✓ SRM Check Passed: The randomization appears to be working correctly.")
        else:
            st.error(f"✗ SRM Check Failed: {srm_result.warning_message}")
    
    except Exception as e:
        st.error(f"Could not perform SRM check: {e}")
    
    # AA Test Check (if pretest data is available)
    if pretest_data is not None:
        st.write("#### AA Test Check")
        
        try:
            # Check if we have an experiment column in pretest data
            if 'experiment' in pretest_data.columns:
                # Filter to only AA test data
                aa_data = pretest_data[pretest_data['experiment'] == 'AA_test']
                
                if len(aa_data) > 0:
                    # Get control and treatment groups
                    aa_control = aa_data[aa_data[group_col] == control_value][conversion_col]
                    aa_treatment = aa_data[aa_data[group_col] == treatment_value][conversion_col]
                    
                    # Perform AA test
                    aa_result = aa_test(
                        control_group=aa_control,
                        treatment_group=aa_treatment,
                        metric_type="binary"
                    )
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("AA Control Rate", f"{aa_control.mean():.4f}")
                        st.metric("AA Treatment Rate", f"{aa_treatment.mean():.4f}")
                    
                    with col2:
                        st.metric("p-value", f"{aa_result.p_value:.4f}")
                        st.metric("Test Statistic", f"{aa_result.statistic:.4f}")
                    
                    # Display pass/fail message
                    if aa_result.passed:
                        st.success("✓ AA Test Passed: No significant difference found between control groups.")
                    else:
                        st.error(f"✗ AA Test Failed: {aa_result.warning_message}")
                else:
                    st.warning("No AA test data found in the pretest dataset.")
            else:
                st.warning("No 'experiment' column found in pretest data for AA test identification.")
        
        except Exception as e:
            st.error(f"Could not perform AA test: {e}")
    else:
        st.info("No pretest data available for AA test validation.")


def render_interpretation() -> None:
    """Renders the interpretation and recommendation section."""
    st.subheader("Interpretation & Recommendations")
    
    # Check if we have test results
    if 'test_result' not in st.session_state:
        st.warning("Run the statistical test first to get interpretation.")
        return
    
    result = st.session_state['test_result']
    
    # Create a box with the main interpretation
    with st.container():
        st.markdown("### Test Result")
        
        # Decision based on significance
        if result.significant:
            if result.difference > 0:
                st.success("**The test is conclusive. Treatment outperforms Control.**")
                recommendation = "We recommend implementing the Treatment variant."
            else:
                st.error("**The test is conclusive. Treatment underperforms Control.**")
                recommendation = "We recommend keeping the Control variant."
        else:
            st.info("**The test is inconclusive. No significant difference detected.**")
            
            # Add nuance based on observed difference
            if abs(result.relative_difference) < 1:
                recommendation = "The variants perform similarly. Choose based on other factors."
            elif result.difference > 0:
                recommendation = "Treatment shows a positive trend, but is not statistically significant. Consider extending the test."
            else:
                recommendation = "Treatment shows a negative trend, but is not statistically significant. Consider keeping Control."
        
        st.markdown(f"**Recommendation:** {recommendation}")
    
    # Add details about the effect size
    with st.expander("Effect Size Analysis", expanded=True):
        if result.relative_difference != np.inf:
            st.write(f"**Relative Effect:** {result.relative_difference:.2f}%")
        
        st.write(f"**Absolute Difference:** {result.difference:.6f}")
        
        # Practical significance assessment
        practical_threshold = 0.01  # 1% difference, can be made configurable
        
        if abs(result.difference) < practical_threshold:
            st.info(f"The observed difference ({result.difference:.4f}) is smaller than the practical significance threshold ({practical_threshold}).")
        else:
            st.success(f"The observed difference ({result.difference:.4f}) exceeds the practical significance threshold ({practical_threshold}).")
    
    # Add additional considerations
    with st.expander("Additional Considerations", expanded=False):
        st.write("""
        **Consider these factors when making your decision:**
        
        1. **Business impact:** Calculate the potential revenue or cost impact of implementing the change.
        
        2. **Implementation cost:** Consider the cost and effort required to implement the treatment.
        
        3. **Long-term effects:** Consider if the test duration was sufficient to capture long-term effects.
        
        4. **Segment analysis:** Consider if the effect varies across different user segments.
        
        5. **Experiment validity:** Review validation checks to ensure the experiment was conducted properly.
        """) 