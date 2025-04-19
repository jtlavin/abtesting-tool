"""
Experiment validation module for AB testing.

This module provides functions for validating AB test setups and results,
including AA tests and sample ratio mismatch (SRM) checks.
"""
from typing import Dict, Tuple, Optional, Union, List, Any
import numpy as np
import scipy.stats as stats
import pandas as pd
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Results of an experiment validation test.

    Attributes:
        test_type: Type of validation test performed
        p_value: The p-value of the test
        statistic: The test statistic
        passed: Boolean indicating if the validation passed
        warning_message: Optional warning message if validation failed
    """
    test_type: str
    p_value: float
    statistic: float
    passed: bool
    warning_message: Optional[str] = None


def aa_test(
    control_group: pd.Series,
    treatment_group: pd.Series,
    alpha: float = 0.05,
    metric_type: str = "binary"
) -> ValidationResult:
    """Performs an AA test to check if there are underlying differences between groups.
    
    An AA test compares two control groups to ensure randomization is working properly.
    The null hypothesis is that there is no difference between groups.
    
    Args:
        control_group: Data from first control group
        treatment_group: Data from second control group (actually another control)
        alpha: Significance level (default: 0.05)
        metric_type: Type of metric, either "binary" or "continuous"
        
    Returns:
        ValidationResult: Results of the AA test validation
    """
    if metric_type == "binary":
        # For binary metrics (proportions)
        control_successes = control_group.sum()
        control_size = len(control_group)
        treatment_successes = treatment_group.sum()
        treatment_size = len(treatment_group)
        
        # Calculate proportions
        p_control = control_successes / control_size
        p_treatment = treatment_successes / treatment_size
        
        # Calculate pooled proportion and standard error
        p_pooled = (control_successes + treatment_successes) / (control_size + treatment_size)
        se = np.sqrt(p_pooled * (1 - p_pooled) * (1/control_size + 1/treatment_size))
        
        # Calculate z-statistic
        z_stat = (p_treatment - p_control) / se
        
        # Calculate two-sided p-value
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
        
        # Determine if the validation passed
        passed = p_value >= alpha
        
        warning_message = None
        if not passed:
            warning_message = (
                f"AA test failed (p-value = {p_value:.4f}). "
                f"There may be an underlying difference between groups "
                f"(control: {p_control:.4f}, treatment: {p_treatment:.4f})."
            )
        
        return ValidationResult(
            test_type="AA Test (Binary)",
            p_value=p_value,
            statistic=z_stat,
            passed=passed,
            warning_message=warning_message
        )
    
    elif metric_type == "continuous":
        # For continuous metrics
        t_stat, p_value = stats.ttest_ind(
            treatment_group, 
            control_group, 
            equal_var=False,  # Use Welch's t-test by default
            alternative="two-sided"
        )
        
        # Calculate means
        control_mean = np.mean(control_group)
        treatment_mean = np.mean(treatment_group)
        
        # Determine if the validation passed
        passed = p_value >= alpha
        
        warning_message = None
        if not passed:
            warning_message = (
                f"AA test failed (p-value = {p_value:.4f}). "
                f"There may be an underlying difference between groups "
                f"(control mean: {control_mean:.4f}, treatment mean: {treatment_mean:.4f})."
            )
        
        return ValidationResult(
            test_type="AA Test (Continuous)",
            p_value=p_value,
            statistic=t_stat,
            passed=passed,
            warning_message=warning_message
        )
    
    else:
        raise ValueError("metric_type must be either 'binary' or 'continuous'")


def sample_ratio_mismatch(
    control_size: int,
    treatment_size: int,
    expected_ratio: float = 0.5,
    alpha: float = 0.05
) -> ValidationResult:
    """Checks for sample ratio mismatch (SRM) in AB test group assignment.
    
    SRM occurs when the actual ratio of users in control vs treatment differs
    significantly from the expected ratio, which can indicate a problem with
    randomization or data processing.
    
    Args:
        control_size: Number of users in control group
        treatment_size: Number of users in treatment group
        expected_ratio: Expected proportion of users in treatment group (default: 0.5)
        alpha: Significance level (default: 0.05)
        
    Returns:
        ValidationResult: Results of the SRM check
    """
    total_size = control_size + treatment_size
    
    # Expected counts
    expected_treatment = total_size * expected_ratio
    expected_control = total_size * (1 - expected_ratio)
    
    # Chi-square test (using a 1-degree of freedom goodness-of-fit test)
    observed = np.array([control_size, treatment_size])
    expected = np.array([expected_control, expected_treatment])
    
    chi2_stat, p_value = stats.chisquare(observed, expected)
    
    # Determine if the validation passed
    passed = p_value >= alpha
    
    warning_message = None
    if not passed:
        actual_ratio = treatment_size / total_size
        warning_message = (
            f"Sample Ratio Mismatch detected (p-value = {p_value:.4f}). "
            f"Expected ratio: {expected_ratio:.2f}, Actual ratio: {actual_ratio:.2f}. "
            f"Control size: {control_size}, Treatment size: {treatment_size}."
        )
    
    return ValidationResult(
        test_type="Sample Ratio Mismatch",
        p_value=p_value,
        statistic=chi2_stat,
        passed=passed,
        warning_message=warning_message
    ) 