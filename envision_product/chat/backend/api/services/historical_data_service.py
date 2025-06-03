import pandas as pd
import numpy as np
import os
from typing import Optional, List, Dict, Any
from pydantic import ValidationError
import logging

from ..models import HistoricalDataRequest, HistoricalRecord, HistoricalDataResponse

logger = logging.getLogger(__name__)

# Determine the absolute path to the directory where this service file is located
_SERVICE_DIR = os.path.dirname(os.path.abspath(__file__))
# Construct the default path to the CSV file relative to this service file
# Path will be services_dir/../../data/HistoricalData_v2.csv which resolves correctly
_DEFAULT_DATA_FILE_PATH = os.path.normpath(os.path.join(_SERVICE_DIR, "..", "..", "data", "HistoricalData_v2.csv"))

class HistoricalDataService:
    """Service for managing and querying historical transportation data."""
    
    def __init__(self, data_file_path: str = _DEFAULT_DATA_FILE_PATH):
        """
        Initializes the service and loads the historical data.

        Args:
            data_file_path (str): The path to the CSV data file.
                                  Defaults to a path calculated relative to this script.
        """
        self.data_file = data_file_path
        self.df: Optional[pd.DataFrame] = None
        self._load_data()

    def _load_data(self) -> None:
        """
        Loads historical data from the CSV file into a pandas DataFrame.
        Handles potential file errors and logs them.
        Performs initial data cleaning and normalization.
        """
        try:
            logger.info(f"Attempting to load historical data from: {self.data_file}")
            if not os.path.exists(self.data_file):
                logger.error(f"Historical data file not found at the resolved path: {self.data_file}")
                self.df = pd.DataFrame() # Initialize with an empty DataFrame
                return

            self.df = pd.read_csv(self.data_file)
            logger.info(f"Successfully loaded historical data from {self.data_file} with {len(self.df)} records.")
            
            # Basic data cleaning and normalization
            # Normalize column names to lowercase for easier access
            self.df.columns = [col.lower() for col in self.df.columns]
            
            # Normalize city names (simple stripping and uppercasing for now)
            for col in ['source_city', 'dest_city']:
                if col in self.df.columns:
                    self.df[col] = self.df[col].astype(str).str.strip().str.upper()
            
            # Normalize state and country codes (strip and uppercase)
            for col in ['source_state', 'source_country', 'dest_state', 'dest_country', 'tmode']:
                if col in self.df.columns:
                     self.df[col] = self.df[col].astype(str).str.strip().str.upper()
            
            # Ensure numeric columns are numeric, coercing errors to NaN
            numeric_cols = ['cost_per_lb', 'cost_per_mile', 'cost_per_cuft', 'shp_count']
            for col in numeric_cols:
                if col in self.df.columns:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            
            # Fill NaNs in key string columns with 'UNKNOWN' or similar, or handle as appropriate
            # For now, we rely on Pydantic to handle optional fields if data is missing.
            
        except FileNotFoundError:
            logger.error(f"Historical data file not found: {self.data_file}")
            self.df = pd.DataFrame()
        except pd.errors.EmptyDataError:
            logger.error(f"Historical data file is empty: {self.data_file}")
            self.df = pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading historical data from {self.data_file}: {e}")
            self.df = pd.DataFrame() # Ensure df is initialized even on error

    def _normalize_city_name(self, city: Optional[str]) -> Optional[str]:
        """
        Normalizes a city name for matching (strip, uppercase).
        
        Args:
            city (Optional[str]): The city name to normalize.
        
        Returns:
            Optional[str]: The normalized city name or None.
        """
        if city is None:
            return None
        return city.strip().upper()

    def _calculate_statistics(self, filtered_df: pd.DataFrame) -> Dict[str, Optional[float]]:
        """
        Calculates cost statistics for the filtered DataFrame.

        Args:
            filtered_df (pd.DataFrame): The DataFrame containing filtered historical records.

        Returns:
            Dict[str, Optional[float]]: A dictionary with average costs.
                                        Returns None for a statistic if it cannot be computed.
        """
        if filtered_df.empty:
            return {
                "avg_cost_per_lb": None,
                "avg_cost_per_mile": None,
                "avg_cost_per_cuft": None,
                "avg_shp_count": None
            }
        
        stats = {
            "avg_cost_per_lb": filtered_df['cost_per_lb'].mean() if 'cost_per_lb' in filtered_df and not filtered_df['cost_per_lb'].isnull().all() else None,
            "avg_cost_per_mile": filtered_df['cost_per_mile'].mean() if 'cost_per_mile' in filtered_df and not filtered_df['cost_per_mile'].isnull().all() else None,
            "avg_cost_per_cuft": filtered_df['cost_per_cuft'].mean() if 'cost_per_cuft' in filtered_df and not filtered_df['cost_per_cuft'].isnull().all() else None,
            "avg_shp_count": filtered_df['shp_count'].mean() if 'shp_count' in filtered_df and not filtered_df['shp_count'].isnull().all() else None
        }
        # Convert NaN to None for JSON compatibility, and round floats
        for key, value in stats.items():
            if pd.isna(value):
                stats[key] = None
            elif isinstance(value, float):
                stats[key] = round(value, 2)
        return stats

    def _get_lane_summary(self, filtered_df: pd.DataFrame, request: HistoricalDataRequest) -> Dict[str, Any]:
        """
        Generates a summary for the queried lane.

        Args:
            filtered_df (pd.DataFrame): The DataFrame containing filtered historical records.
            request (HistoricalDataRequest): The original request parameters.
        
        Returns:
            Dict[str, Any]: A dictionary with lane summary information.
        """
        summary = {
            "route": "N/A",
            "most_common_mode": "N/A",
            "total_shipments_in_data": None
        }

        if request.source_city and request.dest_city:
            source_city_norm = self._normalize_city_name(request.source_city)
            dest_city_norm = self._normalize_city_name(request.dest_city)
            summary["route"] = f"{source_city_norm} to {dest_city_norm}"
        
        if not filtered_df.empty:
            if 'tmode' in filtered_df.columns and not filtered_df['tmode'].mode().empty:
                summary["most_common_mode"] = filtered_df['tmode'].mode()[0]
            if 'shp_count' in filtered_df.columns:
                 summary["total_shipments_in_data"] = int(filtered_df['shp_count'].sum()) if not pd.isna(filtered_df['shp_count'].sum()) else None


        return summary

    async def query_historical_data(self, request: HistoricalDataRequest) -> HistoricalDataResponse:
        """
        Queries historical data based on lane information and other criteria.

        Args:
            request (HistoricalDataRequest): The request model containing query parameters.

        Returns:
            HistoricalDataResponse: The response model containing matching records and statistics.
        """
        if self.df is None or self.df.empty:
            logger.warning("Historical data is not loaded or is empty. Returning empty response.")
            return HistoricalDataResponse(
                records=[],
                total_count=0,
                lane_summary={"route": "N/A", "most_common_mode": "N/A", "total_shipments_in_data": 0},
                cost_statistics=self._calculate_statistics(pd.DataFrame()),
                query_parameters=request
            )

        filtered_df = self.df.copy()

        # Apply filters based on request parameters
        if request.source_city:
            norm_source_city = self._normalize_city_name(request.source_city)
            filtered_df = filtered_df[filtered_df['source_city'] == norm_source_city]
        if request.source_state:
            filtered_df = filtered_df[filtered_df['source_state'] == request.source_state.upper()]
        if request.source_country: # Default is 'US' in model
            filtered_df = filtered_df[filtered_df['source_country'] == request.source_country.upper()]
        
        if request.dest_city:
            norm_dest_city = self._normalize_city_name(request.dest_city)
            filtered_df = filtered_df[filtered_df['dest_city'] == norm_dest_city]
        if request.dest_state:
            filtered_df = filtered_df[filtered_df['dest_state'] == request.dest_state.upper()]
        if request.dest_country: # Default is 'US' in model
            filtered_df = filtered_df[filtered_df['dest_country'] == request.dest_country.upper()]

        if request.transport_mode:
            filtered_df = filtered_df[filtered_df['tmode'] == request.transport_mode.upper()]
        
        total_count = len(filtered_df)
        
        # Sort by shipment count (descending) or other relevant criteria if available
        if 'shp_count' in filtered_df.columns:
            filtered_df = filtered_df.sort_values(by='shp_count', ascending=False).head(request.limit)
        else:
            filtered_df = filtered_df.head(request.limit)

        records_data = []
        for _, row in filtered_df.iterrows():
            # Pydantic will use aliases defined in HistoricalRecord for mapping
            # Ensure all required fields for HistoricalRecord are present or handled
            record_dict = row.rename({ # Ensure mapping to model field names if aliases are not enough or for clarity
                'tmode': 'TMODE',
                'cost_per_lb': 'COST_PER_LB',
                'cost_per_mile': 'COST_PER_MILE',
                'cost_per_cuft': 'COST_PER_CUFT',
                'shp_count': 'SHP_COUNT',
                'mode_preference': 'MODE_PREFERENCE'
            }).to_dict()
            
            # Ensure required fields are not NaN before passing to Pydantic model
            # Pydantic will raise error if required fields are missing.
            # Here, we ensure that if a field is required in the model, it has a value.
            # For optional fields, NaN will be converted to None by Pydantic if the type is Optional[float/int].
            
            # Example of explicit handling for required string fields if they could be NaN:
            for req_str_field in ['source_city', 'source_state', 'source_country', 'dest_city', 'dest_state', 'dest_country', 'TMODE']:
                 if req_str_field in record_dict and pd.isna(record_dict[req_str_field]):
                      record_dict[req_str_field] = "UNKNOWN" # Or handle error appropriately

            try:
                records_data.append(HistoricalRecord(**record_dict))
            except ValidationError as e:
                logger.warning(f"Skipping record due to validation error: {e}. Record data: {record_dict}")
                # Potentially add more detailed logging or error handling here
        
        cost_stats = self._calculate_statistics(filtered_df) # Calculate stats on the limited (top N) data
        lane_summary = self._get_lane_summary(filtered_df, request) # Summary also on limited data

        return HistoricalDataResponse(
            records=records_data,
            total_count=total_count, # This should be count *before* applying limit
            lane_summary=lane_summary,
            cost_statistics=cost_stats,
            query_parameters=request
        )

# Example usage (for testing purposes, not part of the class)
if __name__ == '__main__':
    # Configure basic logging for testing
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # The default path in __init__ is now robust, so direct instantiation should work if this script is run
    # from within its directory or a parent, assuming the relative structure is maintained.
    # For this test, we rely on the new default path calculation.
    test_service = HistoricalDataService() 
    
    if test_service.df is not None and not test_service.df.empty:
        logger.info(f"Test service initialized. DataFrame has {len(test_service.df)} rows.")
        logger.info(f"Columns: {test_service.df.columns.tolist()}")
        
        # Test query
        async def run_test_query():
            test_request = HistoricalDataRequest(
                source_city="DELTA", 
                source_state="BC", 
                source_country="CA",
                dest_city="CALGARY",
                dest_state="AB",
                dest_country="CA",
                limit=5
            )
            response = await test_service.query_historical_data(test_request)
            logger.info(f"Test Query Response: Found {response.total_count} records. Displaying {len(response.records)}.")
            for rec in response.records:
                logger.info(rec.model_dump_json(indent=2))
            logger.info(f"Lane Summary: {response.lane_summary}")
            logger.info(f"Cost Stats: {response.cost_statistics}")

        import asyncio
        asyncio.run(run_test_query())
        
        # Test with a more generic query
        async def run_generic_query():
            generic_request = HistoricalDataRequest(source_city="CHICAGO", limit=3)
            response = await test_service.query_historical_data(generic_request)
            logger.info(f"Generic Query Response: Found {response.total_count} records. Displaying {len(response.records)}.")
            for rec in response.records:
                logger.info(rec.model_dump_json(indent=2))
        asyncio.run(run_generic_query())

    else:
        logger.error("Test service DataFrame is empty or not loaded. Check path and file.")
