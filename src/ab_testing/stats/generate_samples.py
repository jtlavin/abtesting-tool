import numpy as np


def generate_normal_samples(mean: float, std: float, size: int) -> np.ndarray:
    """
    Generate samples from a normal distribution.
    
    Args:
        mean: Mean of the distribution
        std: Standard deviation of the distribution
        size: Number of samples to generate
        
    Returns:
        Array of generated samples
    """
    return np.random.normal(loc=mean, scale=std, size=size)


def generate_binomial_samples(prob: float, size: int) -> np.ndarray:
    """
    Generate samples from a binomial distribution (0 or 1).
    
    Args:
        prob: Probability of success (1)
        size: Number of samples to generate
        
    Returns:
        Array of generated samples
    """
    return np.random.binomial(n=1, p=prob, size=size)