"""
Terminal-Based Neural Network Trainer
Data Handling Component - Updated with better categorical handling
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

class DataHandler:
    """
    Handles data-related tasks including reading CSV files, parsing data, 
    handling missing values, scaling, and encoding features.
    """
    
    def __init__(self):
        """Initialize the DataHandler."""
        self.df = None
        self.target_feature = None
        self.preprocessing_pipeline = None
        self.label_encoder = None
        self.input_features = None
        self.is_classification = None
        
    def load_csv(self, filename):
        """
        Load a CSV file into a DataFrame.
        
        Args:
            filename (str): Path to the CSV file
            
        Returns:
            tuple: (success, columns or error message)
        """
        try:
            self.df = pd.read_csv(filename)
            # Clean column names (remove whitespace)
            self.df.columns = self.df.columns.str.strip()
            return True, list(self.df.columns)
        except Exception as e:
            return False, str(e)
    
    def set_target_feature(self, target_feature):
        """
        Set the target feature for model training.
        
        Args:
            target_feature (str): The column name to use as target
            
        Returns:
            bool: True if successful, False otherwise
        """
        if target_feature in self.df.columns:
            self.target_feature = target_feature
            
            # Determine if classification or regression
            target_data = self.df[target_feature]
            
            # Check if the column is categorical/object type
            if pd.api.types.is_object_dtype(target_data) or pd.api.types.is_categorical_dtype(target_data):
                self.is_classification = True
            else:
                # For numeric columns, check number of unique values
                unique_values = target_data.nunique()
                # Heuristic: if fewer than 10 unique values and they're all integers, likely classification
                if unique_values < 10 and np.all(target_data.dropna().apply(lambda x: float(x) == int(float(x)))):
                    self.is_classification = True
                else:
                    self.is_classification = False
                
            return True
        return False
    
    def set_input_features(self, input_features):
        """
        Set the input features for model training.
        
        Args:
            input_features (list): List of column names to use as inputs
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Verify all features exist in the DataFrame
        if not all(feature in self.df.columns for feature in input_features):
            return False
            
        self.input_features = input_features
        return True
    
    def preprocess_data(self):
        """
        Preprocess the data for model training, handling missing values,
        scaling numerical features, and encoding categorical features.
        
        Returns:
            tuple: (X_processed, y) - processed features and target
        """
        if self.target_feature is None:
            raise ValueError("Target feature must be set before preprocessing.")
            
        # Identify input features if not explicitly set
        if self.input_features is None:
            self.input_features = [col for col in self.df.columns if col != self.target_feature]
            
        # Separate features and target
        X = self.df[self.input_features].copy()
        y = self.df[self.target_feature].copy()
        
        # Handle the target variable first for classification
        if self.is_classification:
            # Initialize label encoder for the target
            self.label_encoder = LabelEncoder()
            y = self.label_encoder.fit_transform(y)
            print(f"Encoded target feature '{self.target_feature}' with classes: {list(self.label_encoder.classes_)}")
        
        # Identify numeric and categorical columns in features
        numeric_features = []
        categorical_features = []
        
        for col in X.columns:
            if pd.api.types.is_numeric_dtype(X[col]):
                numeric_features.append(col)
            else:
                categorical_features.append(col)
        
        # Create preprocessing transformers
        transformers = []
        
        # Add numeric transformer if we have numeric features
        if numeric_features:
            numeric_transformer = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy='mean')),
                ('scaler', StandardScaler())
            ])
            transformers.append(('num', numeric_transformer, numeric_features))
        
        # Add categorical transformer if we have categorical features
        if categorical_features:
            categorical_transformer = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('encoder', OneHotEncoder(handle_unknown='ignore'))
            ])
            transformers.append(('cat', categorical_transformer, categorical_features))
        
        # Create and fit the preprocessing pipeline
        self.preprocessing_pipeline = ColumnTransformer(transformers=transformers)
        
        # Transform the features
        X_processed = self.preprocessing_pipeline.fit_transform(X)
        
        print(f"Preprocessed data: {X_processed.shape[0]} samples, {X_processed.shape[1]} features")
        
        return X_processed, y
    
    def get_feature_info(self):
        """
        Get information about the features in the dataset.
        
        Returns:
            dict: Dictionary with feature information
        """
        if self.df is None:
            return {"error": "No data loaded"}
            
        info = {
            "total_rows": len(self.df),
            "total_columns": len(self.df.columns),
            "missing_values": self.df.isnull().sum().sum(),
            "numeric_columns": list(self.df.select_dtypes(include=['int64', 'float64']).columns),
            "categorical_columns": list(self.df.select_dtypes(include=['object', 'category', 'bool']).columns),
            "target_feature": self.target_feature,
            "is_classification": self.is_classification if self.is_classification is not None else "Unknown",
        }
        
        if self.target_feature:
            if self.is_classification:
                info["target_classes"] = len(self.df[self.target_feature].unique())
                info["class_distribution"] = self.df[self.target_feature].value_counts().to_dict()
            else:
                info["target_min"] = float(self.df[self.target_feature].min())
                info["target_max"] = float(self.df[self.target_feature].max())
                info["target_mean"] = float(self.df[self.target_feature].mean())
        
        return info