"""
Experiment parameter models for AB Testing application.

This module provides data structures for experiment configuration parameters.
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class ExperimentParams:
    """
    Data class for storing experiment parameters.
    
    Attributes:
        alpha: Significance level (Type I error probability)
        power: Statistical power (1 minus Type II error probability)
        mde: Minimum detectable effect
        baseline_rate: Baseline conversion rate (control group)
    """
    alpha: float = 0.05
    power: float = 0.80
    mde: float = 0.10
    baseline_rate: float = 0.10
    
    def validate(self) -> Dict[str, str]:
        """
        Validate experiment parameters.
        
        Returns:
            Dictionary of error messages, empty if all parameters are valid
        """
        errors: Dict[str, str] = {}
        
        if not 0 < self.alpha < 1:
            errors['alpha'] = "Alpha must be between 0 and 1"
        
        if not 0 < self.power < 1:
            errors['power'] = "Power must be between 0 and 1"
            
        if not 0 < self.mde < 1:
            errors['mde'] = "MDE must be between 0 and 1"
            
        if not 0 < self.baseline_rate < 1:
            errors['baseline_rate'] = "Baseline rate must be between 0 and 1"
            
        return errors
    
    def treatment_rate(self) -> float:
        """
        Calculate the treatment conversion rate based on baseline and MDE.
        
        Returns:
            Expected treatment conversion rate
        """
        return self.baseline_rate * (1 + self.mde)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert parameters to dictionary.
        
        Returns:
            Dictionary representation of parameters
        """
        return {
            'alpha': self.alpha,
            'power': self.power,
            'mde': self.mde,
            'baseline_rate': self.baseline_rate,
            'treatment_rate': self.treatment_rate()
        } 