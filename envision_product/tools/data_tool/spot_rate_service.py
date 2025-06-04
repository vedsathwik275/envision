"""
Spot Rate Service for managing and querying spot rate data with 7-day projections.

This service handles loading spot rate data from CSV files and generating
7-day rate matrices for carriers on specified lanes.
"""
import pandas as pd
import numpy as np
import os
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

# Determine the absolute path to the directory where this service file is located
_SERVICE_DIR = os.path.dirname(os.path.abspath(__file__))
# Construct the default path to the CSV file relative to this service file
_DEFAULT_DATA_FILE_PATH = os.path.normpath(os.path.join(_SERVICE_DIR, "data", "SPOT_RATE_V1.csv"))

class SpotRateService:
    """Service for managing and querying spot rate data with 7-day projections."""
    
    def __init__(self, data_file_path: str = _DEFAULT_DATA_FILE_PATH):
        """
        Initializes the service and loads the spot rate data.

        Args:
            data_file_path (str): The path to the CSV data file.
                                  Defaults to a path calculated relative to this script.
        """
        self.data_file = data_file_path
        self.df: Optional[pd.DataFrame] = None
        self._load_data()

    def _load_data(self) -> None:
        """
        Loads spot rate data from the CSV file into a pandas DataFrame.
        Handles potential file errors and logs them.
        Performs initial data cleaning and normalization.
        """
        try:
            logger.info(f"Attempting to load spot rate data from: {self.data_file}")
            if not os.path.exists(self.data_file):
                logger.error(f"Spot rate data file not found at the resolved path: {self.data_file}")
                self.df = pd.DataFrame() # Initialize with an empty DataFrame
                return

            self.df = pd.read_csv(self.data_file)
            logger.info(f"Successfully loaded spot rate data from {self.data_file} with {len(self.df)} records.")
            
            # Basic data cleaning and normalization
            # Normalize column names to lowercase for easier access
            self.df.columns = [col.lower() for col in self.df.columns]
            
            # Normalize city names (simple stripping and uppercasing for now)
            for col in ['source_city', 'dest_city']:
                if col in self.df.columns:
                    self.df[col] = self.df[col].astype(str).str.strip().str.upper()
            
            # Normalize state, country codes, transport mode, and carrier (strip and uppercase)
            for col in ['source_state', 'source_country', 'dest_state', 'dest_country', 'tmode', 'carrier']:
                if col in self.df.columns:
                     self.df[col] = self.df[col].astype(str).str.strip().str.upper()
            
            # Ensure numeric columns are numeric, coercing errors to NaN
            numeric_cols = ['spot_rate', 'distance', 'cost_per_mile']
            for col in numeric_cols:
                if col in self.df.columns:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            
        except FileNotFoundError:
            logger.error(f"Spot rate data file not found: {self.data_file}")
            self.df = pd.DataFrame()
        except pd.errors.EmptyDataError:
            logger.error(f"Spot rate data file is empty: {self.data_file}")
            self.df = pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading spot rate data from {self.data_file}: {e}")
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

    def _generate_date_range(self, shipment_date: str, days: int = 7) -> List[str]:
        """
        Generates a list of consecutive dates starting from the shipment date.
        
        Args:
            shipment_date (str): Base shipment date in YYYY-MM-DD format.
            days (int): Number of days to generate (default 7).
        
        Returns:
            List[str]: List of dates in YYYY-MM-DD format.
        """
        try:
            base_date = datetime.strptime(shipment_date, "%Y-%m-%d").date()
            return [(base_date + timedelta(days=i)).isoformat() for i in range(days)]
        except ValueError as e:
            logger.error(f"Invalid date format: {shipment_date}. Expected YYYY-MM-DD. Error: {e}")
            raise ValueError(f"Invalid date format: {shipment_date}. Expected YYYY-MM-DD format.")

    def _generate_rate_variance(self, base_rate: float, num_days: int = 6) -> List[float]:
        """
        Generates rate variations using ±5% uniform distribution.
        
        Args:
            base_rate (float): The base spot rate to vary from.
            num_days (int): Number of additional days to generate (default 6).
        
        Returns:
            List[float]: List of varied rates rounded to 2 decimal places.
        """
        if base_rate <= 0:
            logger.warning(f"Base rate is non-positive: {base_rate}. Using absolute value.")
            base_rate = abs(base_rate)
        
        variance_range = base_rate * 0.05  # ±5%
        min_rate = max(0.01, base_rate - variance_range)  # Ensure rates stay positive
        max_rate = base_rate + variance_range
        
        # Generate varied rates using uniform distribution
        varied_rates = np.random.uniform(min_rate, max_rate, num_days)
        
        # Round to 2 decimal places and convert to list
        return [round(rate, 2) for rate in varied_rates]

    def _filter_by_lane(self, filtered_df: pd.DataFrame, request) -> pd.DataFrame:
        """
        Applies lane filters to the DataFrame based on request parameters.
        
        Args:
            filtered_df (pd.DataFrame): DataFrame to filter.
            request: Request containing filter parameters.
        
        Returns:
            pd.DataFrame: Filtered DataFrame.
        """
        # Apply filters based on request parameters
        if request.source_city:
            norm_source_city = self._normalize_city_name(request.source_city)
            filtered_df = filtered_df[filtered_df['source_city'] == norm_source_city]
        if request.source_state:
            filtered_df = filtered_df[filtered_df['source_state'] == request.source_state.upper()]
        if request.source_country:
            filtered_df = filtered_df[filtered_df['source_country'] == request.source_country.upper()]
        
        if request.dest_city:
            norm_dest_city = self._normalize_city_name(request.dest_city)
            filtered_df = filtered_df[filtered_df['dest_city'] == norm_dest_city]
        if request.dest_state:
            filtered_df = filtered_df[filtered_df['dest_state'] == request.dest_state.upper()]
        if request.dest_country:
            filtered_df = filtered_df[filtered_df['dest_country'] == request.dest_country.upper()]
        
        return filtered_df

    async def query_spot_rate_matrix(self, request):
        """
        Queries spot rate data and generates a 7-day rate matrix for each carrier.

        Args:
            request: The request model containing query parameters.

        Returns:
            The response model containing carrier cost details.
        """
        if self.df is None or self.df.empty:
            logger.warning("Spot rate data is not loaded or is empty.")
            raise ValueError("Spot rate data is not available.")

        filtered_df = self._filter_by_lane(self.df.copy(), request)

        if filtered_df.empty:
            logger.info(f"No carriers found for the specified lane: {request.model_dump_json()}")
            raise ValueError("No carriers found for the specified lane parameters.")

        # Generate date range for 7 days
        date_range = self._generate_date_range(request.shipment_date)
        
        # Extract lane information for response
        origin_city = self._normalize_city_name(request.source_city) or "UNKNOWN"
        origin_state = request.source_state.upper() if request.source_state else "UNKNOWN"
        destination_city = self._normalize_city_name(request.dest_city) or "UNKNOWN"
        destination_state = request.dest_state.upper() if request.dest_state else "UNKNOWN"
        shipment_date_formatted = self._convert_date_format(request.shipment_date)
        
        # Group by carrier (without transport mode in the grouping since we'll include it in cost details)
        carriers_data = []
        
        for carrier, carrier_df in filtered_df.groupby('carrier'):
            cost_details = []
            
            # For each transport mode this carrier offers
            for tmode, tmode_df in carrier_df.groupby('tmode'):
                # Use the first spot rate for this carrier-tmode combination as base rate
                base_rate = float(tmode_df['spot_rate'].iloc[0])
                
                # Generate 6 additional days with variance
                varied_rates = self._generate_rate_variance(base_rate)
                
                # Combine base rate (day 1) with varied rates (days 2-7)
                all_rates = [round(base_rate, 2)] + varied_rates
                
                # Generate quote ID for this carrier-mode combination
                quote_id = self._generate_quote_id()
                
                # Create cost details for each date - import these from main.py
                from .main import CostDetail
                
                # Create cost details for each date
                for i, (date_str, rate) in enumerate(zip(date_range, all_rates)):
                    date_formatted = self._convert_date_format(date_str)
                    
                    # For demo purposes, we'll use the spot rate as line haul
                    # and set fuel to 0 since we don't have separate breakdown
                    cost_details.append(CostDetail(
                        ship_date=date_formatted,
                        total_spot_cost=str(rate),
                        cost_currency="USD",
                        line_haul=str(rate),
                        fuel="0",
                        quote_id=quote_id,
                        transport_mode=tmode
                    ))
            
            from .main import CarrierSpotCost
            carriers_data.append(CarrierSpotCost(
                carrier=carrier,
                cost_details=cost_details
            ))

        # Sort carriers alphabetically for consistent output
        carriers_data.sort(key=lambda x: x.carrier)

        from .main import SpotRateMatrixResponse
        return SpotRateMatrixResponse(
            origin_city=origin_city,
            origin_state=origin_state,
            destination_city=destination_city,
            destination_state=destination_state,
            shipment_date=shipment_date_formatted,
            spot_costs=carriers_data,
            query_parameters=request
        )

    def _convert_date_format(self, iso_date: str) -> str:
        """
        Converts date from YYYY-MM-DD to MM/DD/YYYY format.
        
        Args:
            iso_date (str): Date in YYYY-MM-DD format.
        
        Returns:
            str: Date in MM/DD/YYYY format.
        """
        try:
            date_obj = datetime.strptime(iso_date, "%Y-%m-%d")
            return date_obj.strftime("%m/%d/%Y")
        except ValueError as e:
            logger.error(f"Invalid date format: {iso_date}. Error: {e}")
            raise ValueError(f"Invalid date format: {iso_date}. Expected YYYY-MM-DD format.")

    def _generate_quote_id(self) -> str:
        """
        Generates a simple quote ID for demo purposes.
        
        Returns:
            str: A simple quote identifier.
        """
        import random
        return f"QUOTE_{random.randint(10000, 99999)}" 