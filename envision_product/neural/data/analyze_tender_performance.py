#!/usr/bin/env python3
"""
TenderPerformance.csv Analysis Script

This script analyzes the TenderPerformance.csv file to extract essential information
for creating a tender performance prediction model.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def analyze_tender_performance(file_path):
    """
    Analyze the tender performance data and print essential information.
    
    Args:
        file_path: Path to the TenderPerformance.csv file
    """
    print(f"Analyzing file: {file_path}")
    print("="*80)
    
    # Load the data
    print("Loading data...")
    df = pd.read_csv(file_path)
    
    # Basic information
    print("\n1. BASIC INFORMATION")
    print("-"*50)
    print(f"Number of records: {len(df)}")
    print(f"Number of columns: {len(df.columns)}")
    print(f"Column names: {', '.join(df.columns)}")
    
    # Data types
    print("\n2. DATA TYPES")
    print("-"*50)
    for col in df.columns:
        print(f"{col}: {df[col].dtype}")
    
    # Check for missing values
    print("\n3. MISSING VALUES")
    print("-"*50)
    missing = df.isnull().sum()
    print(missing[missing > 0] if sum(missing) > 0 else "No missing values")
    
    # Basic statistics of numerical columns
    print("\n4. NUMERICAL STATISTICS")
    print("-"*50)
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns
    if len(numerical_cols) > 0:
        print(df[numerical_cols].describe())
    else:
        print("No numerical columns found")
    
    # Unique values in categorical columns
    print("\n5. CATEGORICAL COLUMNS ANALYSIS")
    print("-"*50)
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        unique_vals = df[col].nunique()
        print(f"{col}: {unique_vals} unique values")
        if unique_vals < 10:  # Only show if there are few unique values
            print(f"Values: {', '.join(map(str, df[col].unique()))}")
        print(f"Top 5 values: {', '.join(map(str, df[col].value_counts().nlargest(5).index))}")
        print("-"*30)
    
    # Time series analysis (if date columns exist)
    print("\n6. TIME SERIES ANALYSIS")
    print("-"*50)
    # Try to identify date columns based on column name
    date_cols = [col for col in df.columns if 'date' in col.lower() or 'month' in col.lower() or 'year' in col.lower()]
    
    if date_cols:
        print(f"Possible date columns: {', '.join(date_cols)}")
        for col in date_cols:
            try:
                # Try to convert to datetime
                if df[col].dtype == 'object':
                    df[f"{col}_dt"] = pd.to_datetime(df[col], errors='coerce')
                    if df[f"{col}_dt"].notnull().all():
                        print(f"Successfully converted {col} to datetime")
                        print(f"Date range: {df[f'{col}_dt'].min()} to {df[f'{col}_dt'].max()}")
                        print(f"Time span: {(df[f'{col}_dt'].max() - df[f'{col}_dt'].min()).days} days")
            except Exception as e:
                print(f"Could not convert {col} to datetime: {str(e)}")
    else:
        print("No obvious date columns found")
    
    # Correlation analysis for numerical columns
    print("\n7. CORRELATION ANALYSIS")
    print("-"*50)
    if len(numerical_cols) > 1:
        correlation = df[numerical_cols].corr()
        print("Correlation matrix:")
        print(correlation)
        
        # Find highly correlated pairs
        high_corr_pairs = []
        for i in range(len(correlation.columns)):
            for j in range(i+1, len(correlation.columns)):
                if abs(correlation.iloc[i, j]) > 0.7:  # Threshold for high correlation
                    high_corr_pairs.append((correlation.columns[i], correlation.columns[j], correlation.iloc[i, j]))
        
        if high_corr_pairs:
            print("\nHighly correlated pairs (abs(corr) > 0.7):")
            for col1, col2, corr in high_corr_pairs:
                print(f"{col1} & {col2}: {corr:.3f}")
        else:
            print("No highly correlated pairs found")
    else:
        print("Not enough numerical columns for correlation analysis")
    
    # Print column names that might be potential targets for prediction
    print("\n8. POTENTIAL TARGET COLUMNS FOR PREDICTION")
    print("-"*50)
    potential_targets = [col for col in numerical_cols if 'performance' in col.lower() 
                        or 'rate' in col.lower() or 'score' in col.lower() 
                        or 'acceptance' in col.lower() or 'ratio' in col.lower()]
    
    if potential_targets:
        print(f"Potential target columns: {', '.join(potential_targets)}")
    else:
        print("No obvious target columns identified. Please inspect the data manually.")
    
    # Summary of features
    print("\n9. FEATURE ENGINEERING SUGGESTIONS")
    print("-"*50)
    print("Based on the observed data, consider:")
    print("- Converting categorical variables to one-hot encoding")
    print("- Normalizing numerical features")
    print("- Creating time-based features if date columns exist (month, quarter, etc.)")
    print("- Creating interaction features between related columns")
    
    print("\n10. MODEL DEVELOPMENT RECOMMENDATIONS")
    print("-"*50)
    print("For this type of data, consider:")
    print("- Neural network with appropriate layers for the data complexity")
    print("- Time series forecasting techniques if temporal patterns exist")
    print("- Including both categorical and numerical features with proper preprocessing")
    
    print("\n"+"="*80)
    print("Analysis complete")

if __name__ == "__main__":
    # Replace this with the actual path to TenderPerformance.csv
    file_path = "TenderPerformance.csv"
    analyze_tender_performance(file_path) 