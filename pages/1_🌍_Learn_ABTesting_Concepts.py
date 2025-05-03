"""
AB Testing Calculator - Learn AB Testing Concepts
"""
import streamlit as st
from src.ab_testing.ui.data_generation import render_data_generation_section
st.set_page_config(page_title="Learn AB Testing Concepts", page_icon="🌍", layout="wide")


# Set title
st.markdown("# Learn AB Testing Concepts")
st.sidebar.header("Learn AB Testing Concepts")


render_data_generation_section()
st.markdown("""
## What is AB Testing?

AB Testing is a statistical method used to compare two versions of a variable, 
typically a website or app, to determine which version performs better. 

## Why AB Testing?

AB Testing is used to determine which version of a variable is better.

## How AB Testing Works

AB Testing works by comparing the performance of two versions of a variable.

## What is a Variable?

A variable is a characteristic of a population that can be measured.

## What is a Population?

A population is a group of people or objects that share a common characteristic.

## What is a Sample?

A sample is a subset of a population that is used to make inferences about the population.

## What is a Sample Size?

A sample size is the number of people or objects in a sample.

## What is a Confidence Interval?

A confidence interval is a range of values that is likely to contain the true value of a population.

## What is a P-Value?

A p-value is the probability that the null hypothesis is true.

## What is a Null Hypothesis?

A null hypothesis is a hypothesis that the two versions of a variable are the same.

## What is an Alternative Hypothesis?

An alternative hypothesis is a hypothesis that the two versions of a variable are different.

## What is a Type I Error?

A type I error is the probability of rejecting the null hypothesis when it is true.

## What is a Type II Error? 

A type II error is the probability of accepting the null hypothesis when it is false.

## What is a Power?

A power is the probability of rejecting the null hypothesis when it is false.   

## What is a T-Test?

A t-test is a statistical test used to compare the means of two groups. 

## What is a Chi-Square Test?

A chi-square test is a statistical test used to compare the proportions of two groups.

## What is a F-Test?

A f-test is a statistical test used to compare the variances of two groups. 

## What is a Z-Test?

A z-test is a statistical test used to compare the means of two groups.  
""")