"""
Data upload UI components for AB Testing application.

This module provides UI components for data upload and preview.
"""
from typing import Tuple, Optional, Dict, Any
import streamlit as st
import pandas as pd
from src.ab_testing.data.loader import load_data, get_data_statistics


def render_data_upload_section() -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    Render the data upload section of the UI.
    
    Returns:
        Tuple containing (pretest_data, test_data)
    """
    st.write("Upload your pretest and test data files in CSV format.")
    
    # Create two columns for file uploaders
    col1, col2 = st.columns(2)
    
    # Initialize return values
    pretest_data = None
    test_data = None
    
    with col1:
        pretest_data = _render_pretest_uploader()
    
    with col2:
        test_data = _render_test_uploader()
        
    return pretest_data, test_data


def _render_pretest_uploader() -> Optional[pd.DataFrame]:
    """
    Render the pretest data uploader.
    
    Returns:
        DataFrame with pretest data or None
    """
    pretest_file = st.file_uploader("Upload Pretest Data (CSV)", type=['csv'])
    pretest_data = None
    
    if pretest_file is not None:
        try:
            pretest_data = load_data(pretest_file)
            st.write("Pretest Data Preview:")
            st.dataframe(pretest_data.head())
            
            # Display basic statistics
            stats = get_data_statistics(pretest_data)
            st.write("Pretest Data Statistics:")
            st.write(f"Number of rows: {stats.get('row_count', 'N/A')}")
            
            if stats.get('date_min') and stats.get('date_max'):
                st.write(f"Date range: {stats.get('date_min').strftime('%Y-%m-%d')} to {stats.get('date_max').strftime('%Y-%m-%d')}")
            
            if stats.get('signup_rate') is not None:
                st.write(f"Sign-up rate: {stats.get('signup_rate'):.2%}")
                
        except Exception as e:
            st.error(f"Error loading pretest data: {str(e)}")
    
    return pretest_data


def _render_test_uploader() -> Optional[pd.DataFrame]:
    """
    Render the test data uploader.
    
    Returns:
        DataFrame with test data or None
    """
    test_file = st.file_uploader("Upload Test Data (CSV)", type=['csv'])
    test_data = None
    
    if test_file is not None:
        try:
            test_data = load_data(test_file)
            st.write("Test Data Preview:")
            st.dataframe(test_data.head())
            
            # Display basic statistics
            stats = get_data_statistics(test_data)
            st.write("Test Data Statistics:")
            st.write(f"Number of rows: {stats.get('row_count', 'N/A')}")
            
            if stats.get('date_min') and stats.get('date_max'):
                st.write(f"Date range: {stats.get('date_min').strftime('%Y-%m-%d')} to {stats.get('date_max').strftime('%Y-%m-%d')}")
            
            if stats.get('signup_rate') is not None:
                st.write(f"Sign-up rate: {stats.get('signup_rate'):.2%}")
                
        except Exception as e:
            st.error(f"Error loading test data: {str(e)}")
    
    return test_data 