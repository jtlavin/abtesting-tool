"""
Data loading and processing functionality for AB Testing application.

This module provides functions to load, validate, and process AB testing data.
"""
from typing import Dict, Optional, Tuple, Union, Any
import pandas as pd
from datetime import datetime


def load_data(file: Any) -> Optional[pd.DataFrame]:
    """
    Load data from an uploaded file into a pandas DataFrame.
    
    Args:
        file: The uploaded file object from streamlit
        
    Returns:
        DataFrame with the loaded data or None if file is invalid
        
    Raises:
        ValueError: If the file format is not supported
    """
    if file is None:
        return None
    
    try:
        df = pd.read_csv(file)
        # Convert date to datetime if it exists
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        raise ValueError(f"Error loading data: {str(e)}")


def get_data_statistics(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate basic statistics from the provided DataFrame.
    
    Args:
        data: DataFrame containing AB test data
        
    Returns:
        Dictionary with basic statistics (rows, date range, signup rate)
    """
    if data is None or data.empty:
        return {}
    
    try:
        stats = {
            "row_count": data.shape[0],
            "date_min": data['date'].min() if 'date' in data.columns else None,
            "date_max": data['date'].max() if 'date' in data.columns else None,
            "signup_rate": data['submitted'].mean() if 'submitted' in data.columns else None
        }
        return stats
    except Exception as e:
        print(f"Error calculating statistics: {str(e)}")
        return {}


def split_test_data(data: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    Split test data into control and treatment groups.
    
    Args:
        data: DataFrame containing AB test data
        
    Returns:
        Tuple containing (control_data, treatment_data)
    """
    if data is None or data.empty:
        return None, None
    
    try:
        control = data[data['group'] == 0] if 'group' in data.columns else None
        treatment = data[data['group'] == 1] if 'group' in data.columns else None
        return control, treatment
    except Exception as e:
        print(f"Error splitting test data: {str(e)}")
        return None, None 