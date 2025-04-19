"""
Statistical hypothesis testing module for AB testing.

This module provides functions for conducting statistical hypothesis tests
and calculating confidence intervals for AB test results.
"""
from typing import Dict, Tuple, Optional, Union, List, Any
import numpy as np
import scipy.stats as stats
from dataclasses import dataclass


@dataclass
class TestResult:
    """Results of a statistical hypothesis test.

    Attributes:
        p_value: The p-value of the test
        statistic: The test statistic
        control_metric: Value of the metric in the control group
        treatment_metric: Value of the metric in the treatment group
        difference: Absolute difference between treatment and control
        relative_difference: Relative difference (as percentage) between treatment and control
        confidence_interval: Tuple containing lower and upper bounds of the confidence interval
        significant: Boolean indicating if the result is statistically significant
        method: The statistical method used for the test
    """
    p_value: float
    statistic: float
    control_metric: float
    treatment_metric: float
    difference: float
    relative_difference: float
    confidence_interval: Tuple[float, float]
    significant: bool
    method: str


def proportion_test(
    control_successes: int,
    control_size: int,
    treatment_successes: int,
    treatment_size: int,
    confidence_level: float = 0.95,
    alternative: str = "two-sided"
) -> TestResult:
    """Performs a z-test for comparing two proportions.

    Args:
        control_successes: Number of successes in the control group
        control_size: Total size of the control group
        treatment_successes: Number of successes in the treatment group
        treatment_size: Total size of the treatment group
        confidence_level: Confidence level (default: 0.95)
        alternative: Alternative hypothesis, one of 'two-sided', 'larger', 'smaller'

    Returns:
        TestResult: Results of the proportion test
    """
    # Calculate proportions
    p_control = control_successes / control_size
    p_treatment = treatment_successes / treatment_size
    
    # Calculate pooled proportion and standard error
    p_pooled = (control_successes + treatment_successes) / (control_size + treatment_size)
    se = np.sqrt(p_pooled * (1 - p_pooled) * (1/control_size + 1/treatment_size))
    
    # Calculate z-statistic
    z_stat = (p_treatment - p_control) / se
    
    # Calculate p-value based on alternative hypothesis
    if alternative == "two-sided":
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
    elif alternative == "larger":  # Treatment larger than control
        p_value = 1 - stats.norm.cdf(z_stat)
    elif alternative == "smaller":  # Treatment smaller than control
        p_value = stats.norm.cdf(z_stat)
    else:
        raise ValueError("Alternative must be one of 'two-sided', 'larger', 'smaller'")
    
    # Calculate confidence interval for the difference
    alpha = 1 - confidence_level
    z_critical = stats.norm.ppf(1 - alpha/2)
    
    # Standard error for difference in proportions
    se_diff = np.sqrt(p_control * (1 - p_control) / control_size + 
                      p_treatment * (1 - p_treatment) / treatment_size)
    
    margin = z_critical * se_diff
    diff = p_treatment - p_control
    ci_lower = diff - margin
    ci_upper = diff + margin
    
    # Calculate relative difference as percentage
    rel_diff = (diff / p_control) * 100 if p_control > 0 else np.inf
    
    # Determine if the result is significant
    significant = p_value < alpha
    
    return TestResult(
        p_value=p_value,
        statistic=z_stat,
        control_metric=p_control,
        treatment_metric=p_treatment,
        difference=diff,
        relative_difference=rel_diff,
        confidence_interval=(ci_lower, ci_upper),
        significant=significant,
        method="proportion_z_test"
    )


def mean_test(
    control_data: np.ndarray,
    treatment_data: np.ndarray,
    confidence_level: float = 0.95,
    alternative: str = "two-sided",
    equal_var: bool = False
) -> TestResult:
    """Performs a t-test for comparing two means.

    Args:
        control_data: Array of values from the control group
        treatment_data: Array of values from the treatment group
        confidence_level: Confidence level (default: 0.95)
        alternative: Alternative hypothesis, one of 'two-sided', 'larger', 'smaller'
        equal_var: Whether to assume equal variance (default: False)

    Returns:
        TestResult: Results of the mean test
    """
    # Perform t-test
    alt_map = {
        "two-sided": "two-sided",
        "larger": "greater",
        "smaller": "less"
    }
    scipy_alternative = alt_map.get(alternative)
    
    if scipy_alternative is None:
        raise ValueError("Alternative must be one of 'two-sided', 'larger', 'smaller'")

    t_stat, p_value = stats.ttest_ind(
        treatment_data, 
        control_data, 
        equal_var=equal_var, 
        alternative=scipy_alternative
    )
    
    # Calculate means
    control_mean = np.mean(control_data)
    treatment_mean = np.mean(treatment_data)
    
    # Calculate confidence interval
    alpha = 1 - confidence_level
    
    # Calculate standard error and degrees of freedom
    n1, n2 = len(treatment_data), len(control_data)
    var1, var2 = np.var(treatment_data, ddof=1), np.var(control_data, ddof=1)
    
    if equal_var:
        # Pooled standard error
        df = n1 + n2 - 2
        pooled_var = ((n1 - 1) * var1 + (n2 - 1) * var2) / df
        se = np.sqrt(pooled_var * (1/n1 + 1/n2))
    else:
        # Welch-Satterthwaite equation
        se = np.sqrt(var1/n1 + var2/n2)
        df = (var1/n1 + var2/n2)**2 / ((var1/n1)**2/(n1-1) + (var2/n2)**2/(n2-1))
    
    # Calculate t-critical value
    t_critical = stats.t.ppf(1 - alpha/2, df)
    
    # Calculate confidence interval
    diff = treatment_mean - control_mean
    margin = t_critical * se
    ci_lower = diff - margin
    ci_upper = diff + margin
    
    # Calculate relative difference as percentage
    rel_diff = (diff / control_mean) * 100 if control_mean != 0 else np.inf
    
    # Determine if the result is significant
    significant = p_value < alpha
    
    return TestResult(
        p_value=p_value,
        statistic=t_stat,
        control_metric=control_mean,
        treatment_metric=treatment_mean,
        difference=diff,
        relative_difference=rel_diff,
        confidence_interval=(ci_lower, ci_upper),
        significant=significant,
        method="mean_t_test"
    )


def is_statistically_significant(
    test_result: TestResult,
    alpha: float = 0.05
) -> bool:
    """Determines if a test result is statistically significant.

    Args:
        test_result: Test result object
        alpha: Significance level (default: 0.05)

    Returns:
        bool: True if the result is statistically significant, False otherwise
    """
    return test_result.p_value < alpha


def format_confidence_interval(ci: Tuple[float, float], decimals: int = 2) -> str:
    """Formats a confidence interval for display.

    Args:
        ci: Tuple containing lower and upper bounds of the confidence interval
        decimals: Number of decimal places to include

    Returns:
        str: Formatted confidence interval string
    """
    return f"[{ci[0]:.{decimals}f}, {ci[1]:.{decimals}f}]" 