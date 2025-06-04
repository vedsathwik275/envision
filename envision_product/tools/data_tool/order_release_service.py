"""Order Release Service for fetching order release data from Oracle Transportation Management."""

import http.client
import json
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class OrderReleaseService:
    """Oracle Transportation Management Order Release API client."""
    
    def __init__(self, base_url: str, auth_token: str) -> None:
        """
        Initialize Order Release service.
        
        Args:
            base_url: Base URL for the Order Release API
            auth_token: Authentication token for API access
        """
        self.base_url = base_url
        self.auth_token = auth_token
        self.endpoint = "/logisticsRestApi/resources-int/v2/orderReleases"
        self.custom_query_endpoint = "/logisticsRestApi/resources-int/v2/custom-actions/queries/orderReleases"
    
    def get_order_release(self, order_release_gid: str) -> Dict[str, Any]:
        """
        Fetch order release data by order release GID.
        
        Args:
            order_release_gid: The order release GID to fetch
            
        Returns:
            Dictionary containing API response or error information
        """
        conn = http.client.HTTPSConnection(self.base_url)
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {self.auth_token}'
        }
        
        # Construct the full endpoint with query parameter
        endpoint_with_params = f"{self.endpoint}/{order_release_gid}"
        
        try:
            conn.request("GET", endpoint_with_params, headers=headers)
            response = conn.getresponse()
            data = response.read()
            
            if response.status == 200:
                return json.loads(data.decode("utf-8"))
            elif response.status == 404:
                return {"error": "Order release not found", "status_code": 404}
            else:
                return {
                    "error": f"API request failed with status {response.status}",
                    "status_code": response.status,
                    "response": data.decode("utf-8") if data else None
                }
                
        except Exception as e:
            return {"error": str(e), "status_code": 500}
        finally:
            conn.close()
    
    def get_unplanned_orders(self, origin_city: str, origin_state: str, origin_country: str,
                           destination_city: str, destination_state: str, destination_country: str) -> Dict[str, Any]:
        """
        Fetch unplanned orders by lane using Oracle Transportation Management custom query.
        
        Args:
            origin_city: Origin city for the lane
            origin_state: Origin state for the lane
            origin_country: Origin country for the lane
            destination_city: Destination city for the lane
            destination_state: Destination state for the lane
            destination_country: Destination country for the lane
            
        Returns:
            Dictionary containing API response or error information
        """
        conn = http.client.HTTPSConnection(self.base_url)
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {self.auth_token}'
        }
        
        # Construct the request payload for custom query
        payload = {
            "copiedFrom": "BSL.UNPLANNED_ORDERS_BY_LANE",
            "parameterValues": {
                "0": origin_city,
                "1": origin_state,
                "2": origin_country,
                "3": destination_city,
                "4": destination_state,
                "5": destination_country
            }
        }
        
        json_payload = json.dumps(payload)
        
        try:
            conn.request("POST", self.custom_query_endpoint, body=json_payload, headers=headers)
            response = conn.getresponse()
            data = response.read()
            
            if response.status == 200:
                return json.loads(data.decode("utf-8"))
            elif response.status == 404:
                return {"error": "No unplanned orders found for the specified lane", "status_code": 404}
            else:
                return {
                    "error": f"API request failed with status {response.status}",
                    "status_code": response.status,
                    "response": data.decode("utf-8") if data else None
                }
                
        except Exception as e:
            return {"error": str(e), "status_code": 500}
        finally:
            conn.close() 