#!/usr/bin/env python3
import os
import json
import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class DataProcessor:
    """Service for processing and previewing data files"""
    
    def __init__(self, preview_path: str = "data/previews"):
        """Initialize the service with preview storage path"""
        self.preview_path = Path(preview_path)
        self.preview_path.mkdir(parents=True, exist_ok=True)
    
    def generate_preview(self, file_id: str, file_path: str) -> Dict[str, Any]:
        """Generate a preview of data from a file
        
        Args:
            file_id: ID of the file
            file_path: Path to the file
            
        Returns:
            Dictionary with preview information
        """
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Get basic information
            total_rows = len(df)
            total_columns = len(df.columns)
            
            # Sample rows (first 10)
            sample_rows = df.head(10).to_dict(orient='records')
            
            # Generate column information
            column_info = {}
            for col in df.columns:
                col_type = str(df[col].dtype)
                column_info[col] = {
                    "type": col_type,
                    "missing": int(df[col].isna().sum())
                }
                
                # Add statistics based on column type
                if np.issubdtype(df[col].dtype, np.number):
                    # Numerical column
                    column_info[col].update({
                        "min": float(df[col].min()) if not pd.isna(df[col].min()) else None,
                        "max": float(df[col].max()) if not pd.isna(df[col].max()) else None,
                        "mean": float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                        "median": float(df[col].median()) if not pd.isna(df[col].median()) else None
                    })
                else:
                    # Categorical/string column
                    value_counts = df[col].value_counts().head(5).to_dict()
                    column_info[col]["top_values"] = {str(k): int(v) for k, v in value_counts.items()}
            
            # Missing data summary
            missing_data = df.isna().sum()
            missing_data_summary = {
                "total_missing": int(missing_data.sum()),
                "columns_with_missing": int((missing_data > 0).sum()),
                "missing_by_column": {col: int(count) for col, count in missing_data.items() if count > 0}
            }
            
            # Create preview object
            preview = {
                "file_id": file_id,
                "total_rows": total_rows,
                "total_columns": total_columns,
                "sample_rows": sample_rows,
                "column_info": column_info,
                "missing_data_summary": missing_data_summary
            }
            
            # Save preview to file
            preview_file = self.preview_path / f"{file_id}.json"
            with open(preview_file, "w") as f:
                json.dump(preview, f, indent=2)
            
            return preview
            
        except Exception as e:
            logger.error(f"Error generating preview for file {file_id}: {str(e)}")
            
            # Return minimal preview with error info
            return {
                "file_id": file_id,
                "total_rows": 0,
                "total_columns": 0,
                "sample_rows": [],
                "column_info": {},
                "error": str(e)
            }
    
    def get_preview(self, file_id: str, file_path: str) -> Optional[Dict[str, Any]]:
        """Get or generate a preview for a file
        
        Args:
            file_id: ID of the file
            file_path: Path to the file
            
        Returns:
            Dictionary with preview data or None if preview cannot be generated
        """
        preview_file = self.preview_path / f"{file_id}.json"
        
        # If preview exists, return it
        if preview_file.exists():
            try:
                with open(preview_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading preview for file {file_id}: {str(e)}")
        
        # Generate new preview
        return self.generate_preview(file_id, file_path)
    
    def read_file(self, file_id: str, file_path: str) -> Optional[pd.DataFrame]:
        """Read a file into a pandas DataFrame
        
        Args:
            file_id: ID of the file
            file_path: Path to the file
            
        Returns:
            DataFrame or None if file cannot be read
        """
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            logger.error(f"Error reading file {file_id}: {str(e)}")
            return None 