#!/usr/bin/env python3
"""
Carrier_Performance_New.csv Analysis Script

This script analyzes the Carrier_Performance_New.csv file to extract essential information
for creating a carrier performance prediction model. The analysis will inform the
development of a neural network to predict carrier performance scores.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

def analyze_carrier_performance(file_path):
    """
    Analyze the carrier performance data and print essential information.
    
    Args:
        file_path: Path to the Carrier_Performance_New.csv file
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
    
    # Analyze carrier performance by source city and destination city
    print("\n6. LANE ANALYSIS")
    print("-"*50)
    
    # Check if relevant columns exist
    lane_cols = [col for col in df.columns if 'source' in col.lower() or 'origin' in col.lower() or 
                'destination' in col.lower() or 'dest' in col.lower()]
    
    if lane_cols:
        print(f"Lane-related columns: {', '.join(lane_cols)}")
        
        # Try to identify source and destination columns
        source_cols = [col for col in lane_cols if 'source' in col.lower() or 'origin' in col.lower()]
        dest_cols = [col for col in lane_cols if 'destination' in col.lower() or 'dest' in col.lower()]
        
        if source_cols and dest_cols:
            # Pick the first source and destination columns
            source_col = source_cols[0]
            dest_col = dest_cols[0]
            
            # Count unique lanes
            df['lane'] = df[source_col] + ' to ' + df[dest_col]
            lane_counts = df['lane'].value_counts()
            
            print(f"Number of unique lanes: {len(lane_counts)}")
            print(f"Top 5 most common lanes: \n{lane_counts.head(5)}")
            
            # If there's a clear carrier column, analyze carrier performance by lane
            carrier_cols = [col for col in df.columns if 'carrier' in col.lower()]
            if carrier_cols:
                carrier_col = carrier_cols[0]
                # Count carriers per lane
                print("\nAverage number of carriers per lane:")
                carriers_per_lane = df.groupby('lane')[carrier_col].nunique()
                print(f"Mean: {carriers_per_lane.mean():.2f}, Min: {carriers_per_lane.min()}, Max: {carriers_per_lane.max()}")
    else:
        print("No lane-related columns identified")
    
    # Time series analysis (if date columns exist)
    print("\n7. TIME SERIES ANALYSIS")
    print("-"*50)
    # Try to identify date columns based on column name
    date_cols = [col for col in df.columns if 'date' in col.lower() or 'month' in col.lower() 
                or 'year' in col.lower() or 'period' in col.lower() or 'quarter' in col.lower()]
    
    if date_cols:
        print(f"Possible date/time period columns: {', '.join(date_cols)}")
        for col in date_cols:
            try:
                # Try to convert to datetime
                if df[col].dtype == 'object':
                    df[f"{col}_dt"] = pd.to_datetime(df[col], errors='coerce')
                    if df[f"{col}_dt"].notnull().sum() > 0:
                        print(f"Successfully converted {col} to datetime for {df[f'{col}_dt'].notnull().sum()} entries")
                        print(f"Date range: {df[f'{col}_dt'].min()} to {df[f'{col}_dt'].max()}")
                        print(f"Time span: {(df[f'{col}_dt'].max() - df[f'{col}_dt'].min()).days} days")
            except Exception as e:
                print(f"Could not convert {col} to datetime: {str(e)}")
    else:
        print("No obvious date columns found")
    
    # Performance metrics analysis
    print("\n8. PERFORMANCE METRICS ANALYSIS")
    print("-"*50)
    
    # Look for performance-related columns
    perf_cols = [col for col in df.columns if any(term in col.lower() for term in 
                ['performance', 'score', 'rating', 'reliability', 'on-time', 'ontime', 
                 'capacity', 'quality', 'communication', 'claims', 'damage'])]
    
    if perf_cols:
        print(f"Performance-related columns: {', '.join(perf_cols)}")
        
        # Analyze each performance metric
        for col in perf_cols:
            if col in numerical_cols:
                print(f"\n{col} Statistics:")
                print(f"Mean: {df[col].mean():.2f}, Median: {df[col].median():.2f}")
                print(f"Min: {df[col].min():.2f}, Max: {df[col].max():.2f}")
                print(f"Standard Deviation: {df[col].std():.2f}")
                
                # Check distribution
                percentiles = np.percentile(df[col].dropna(), [25, 50, 75, 90, 95, 99])
                print(f"Percentiles (25th, 50th, 75th, 90th, 95th, 99th): {', '.join([f'{p:.2f}' for p in percentiles])}")
    else:
        print("No obvious performance metric columns found")
    
    # Correlation analysis for numerical columns
    print("\n9. CORRELATION ANALYSIS")
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
    
    # Try to identify potential target variables
    print("\n10. POTENTIAL TARGET COLUMNS FOR PREDICTION")
    print("-"*50)
    
    # Look for overall performance or composite score columns
    target_keywords = ['overall', 'total', 'composite', 'final', 'performance_score', 'rating']
    potential_targets = [col for col in numerical_cols if any(keyword in col.lower() for keyword in target_keywords)]
    
    if potential_targets:
        print(f"Potential target columns: {', '.join(potential_targets)}")
        for col in potential_targets:
            print(f"\n{col} distribution:")
            print(df[col].describe())
    else:
        perf_cols_subset = [col for col in perf_cols if col in numerical_cols]
        if perf_cols_subset:
            print(f"No clear composite score found. Individual performance metrics that could be targets or combined: {', '.join(perf_cols_subset)}")
        else:
            print("No obvious target columns identified. Please inspect the data manually.")
    
    # Feature engineering suggestions
    print("\n11. FEATURE ENGINEERING SUGGESTIONS")
    print("-"*50)
    print("Based on the analysis, consider:")
    
    print("- Converting categorical variables to one-hot encoding or entity embeddings")
    print("- Normalizing numerical performance metrics to 0-100 scale if they're on different scales")
    
    # Lane-specific suggestions
    if lane_cols:
        print("- Creating lane embeddings to capture lane-specific characteristics")
        print("- Generating lane-carrier interaction features")
    
    # Time-specific suggestions
    if date_cols:
        print("- Extracting temporal features (month, quarter, year, season)")
        print("- Computing rolling averages for performance metrics")
        print("- Creating time-based features to capture seasonality and trends")
    
    # Other suggestions
    print("- Creating composite performance metrics if not already present")
    print("- Developing carrier consistency metrics across different lanes and time periods")
    print("- Calculating performance variance metrics for reliability assessment")
    
    # Neural network recommendations
    print("\n12. NEURAL NETWORK MODEL RECOMMENDATIONS")
    print("-"*50)
    print("For carrier performance prediction, consider:")
    
    print("- Multi-output neural network to predict multiple performance metrics simultaneously")
    print("- Embedding layers for categorical features (carriers, lanes, cities)")
    print("- LSTM or temporal convolutional networks if strong time-series patterns exist")
    print("- Ensemble approach combining predictions for different performance aspects")
    print("- Transfer learning from existing order volume or tender performance models")
    
    print("\nNetwork architecture considerations:")
    print("- Input layer with appropriate dimensions for features")
    print("- Embedding layers for categorical variables")
    print("- Several dense layers with dropout for regularization")
    print("- Multiple output nodes for different performance metrics")
    print("- Custom loss function weighted by business importance of metrics")
    
    print("\n"+"="*80)
    print("Analysis complete")
    print("\nNext steps:")
    print("1. Create a carrier performance model class with appropriate architecture")
    print("2. Implement data preprocessing with standardization and encoding")
    print("3. Develop training pipeline with model evaluation")
    print("4. Integrate with existing API framework for predictions")

def save_summary_report(file_path, output_path="carrier_performance_analysis_report.txt"):
    """
    Runs the analysis and saves the output to a file
    
    Args:
        file_path: Path to the Carrier_Performance_New.csv file
        output_path: Path to save the analysis report
    """
    import sys
    from contextlib import redirect_stdout
    
    with open(output_path, 'w') as f:
        with redirect_stdout(f):
            analyze_carrier_performance(file_path)
    
    print(f"Analysis report saved to {output_path}")

if __name__ == "__main__":
    # Path to the carrier performance data file
    file_path = "Carrier_Performance_New.csv"
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        print(f"Current working directory: {os.getcwd()}")
        print("Please provide the correct path to the Carrier_Performance_New.csv file")
    else:
        # Run analysis and print to console
        analyze_carrier_performance(file_path)
        
        # Optionally save analysis to file
        # save_summary_report(file_path) 