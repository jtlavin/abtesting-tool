"""
Sample size calculation for AB Testing application.

This module provides functions to calculate required sample sizes and related statistics.
"""
from typing import Dict, Tuple, List, Optional
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.power import TTestIndPower, tt_ind_solve_power
from src.ab_testing.models.experiment import ExperimentParams


def calculate_effect_size(p1: float, p2: float) -> float:
    """
    Calculate Cohen's effect size for two proportions.
    
    Args:
        p1: Control group proportion
        p2: Treatment group proportion
        
    Returns:
        Cohen's effect size (d)
    """
    return sm.stats.proportion_effectsize(p1, p2)


def calculate_sample_size(params: ExperimentParams) -> Dict[str, int]:
    """
    Calculate required sample size for AB test based on experiment parameters.
    
    Args:
        params: Experiment parameters
        
    Returns:
        Dictionary with sample size information
    """
    p1 = params.baseline_rate
    p2 = params.treatment_rate()
    
    # Calculate effect size
    effect_size = calculate_effect_size(p1, p2)
    
    # Calculate sample size per group
    n_per_group = tt_ind_solve_power(
        effect_size=effect_size,
        power=params.power,
        alpha=params.alpha
    )
    
    # Round up to nearest thousand
    n_per_group_rounded = int(np.ceil(n_per_group / 1000.0) * 1000)
    
    return {
        "effect_size": effect_size,
        "sample_size_per_group": n_per_group_rounded,
        "total_sample_size": n_per_group_rounded * 2
    }


def calculate_power_curve(params: ExperimentParams, 
                          min_samples: int = 1000, 
                          max_samples: int = 30000, 
                          step: int = 1000) -> Dict[str, List[float]]:
    """
    Calculate power values for a range of sample sizes.
    
    Args:
        params: Experiment parameters
        min_samples: Minimum sample size to consider
        max_samples: Maximum sample size to consider
        step: Step size for sample size range
        
    Returns:
        Dictionary with sample sizes and corresponding power values
    """
    p1 = params.baseline_rate
    p2 = params.treatment_rate()
    effect_size = calculate_effect_size(p1, p2)
    
    sample_sizes = np.arange(min_samples, max_samples + step, step)
    power_analysis = TTestIndPower()
    power_values = [power_analysis.power(
        effect_size=effect_size,
        nobs=n,
        alpha=params.alpha
    ) for n in sample_sizes]
    
    return {
        "sample_sizes": sample_sizes.tolist(),
        "power_values": power_values
    }


def calculate_experiment_duration(
    params: ExperimentParams,
    daily_visitors: int,
    traffic_allocation: float = 1.0
) -> Dict[str, float]:
    """
    Calculate experiment duration based on sample size and traffic.
    
    Args:
        params: Experiment parameters
        daily_visitors: Average number of visitors per day
        traffic_allocation: Percentage of traffic allocated to experiment (0-1)
        
    Returns:
        Dictionary with duration information
    """
    sample_size = calculate_sample_size(params)
    total_required = sample_size["total_sample_size"]
    
    # Calculate daily participants
    daily_participants = daily_visitors * traffic_allocation
    
    # Calculate duration in days
    duration_days = np.ceil(total_required / daily_participants)
    
    return {
        "total_sample_required": total_required,
        "daily_participants": daily_participants,
        "duration_days": duration_days
    } 