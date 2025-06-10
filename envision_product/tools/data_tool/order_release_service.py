"""Order Release Service for fetching order release data from Oracle Transportation Management."""

import http.client
import json
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

import ssl
ssl._create_default_https_context = ssl._create_unverified_context
# only do the above if you are using the mac

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
        self.location_endpoint = "/logisticsRestApi/resources-int/v2/locations"
    
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
    
    def extract_location_urls(self, order_release_data: Dict[str, Any]) -> Dict[str, Optional[str]]:
        """
        Extract canonical href URLs for source and destination locations from order release data.
        
        Args:
            order_release_data: Order release response data from Oracle API
            
        Returns:
            Dictionary with 'source_url' and 'dest_url' keys, values can be None if not found
            
        Example:
            {
                "source_url": "https://otmgtm-test-ejhu.otmgtm.us-ashburn-1.ocs.oraclecloud.com:443/logisticsRestApi/resources-int/v2/locations/BSL.300000001357157-300000054405994",
                "dest_url": "https://otmgtm-test-ejhu.otmgtm.us-ashburn-1.ocs.oraclecloud.com:443/logisticsRestApi/resources-int/v2/locations/BSL.100000086293039"
            }
        """
        result = {"source_url": None, "dest_url": None}
        
        try:
            # Extract source location URL
            source_location = order_release_data.get("sourceLocation", {})
            source_links = source_location.get("links", [])
            if len(source_links) > 1:
                result["source_url"] = source_links[1].get("href")  # canonical link
            
            # Extract destination location URL
            dest_location = order_release_data.get("destinationLocation", {})
            dest_links = dest_location.get("links", [])
            if len(dest_links) > 1:
                result["dest_url"] = dest_links[1].get("href")  # canonical link
                
        except (KeyError, IndexError, TypeError) as e:
            # Handle cases where the expected structure is not present
            pass
            
        return result
    
    def get_location_details(self, location_url: str) -> Dict[str, Any]:
        """
        Fetch detailed location information from a canonical href URL.
        
        Args:
            location_url: Full canonical href URL to the location resource
            
        Returns:
            Dictionary containing location details or error information
            
        Example return:
            {
                "city": "RICHMOND",
                "provinceCode": "VA", 
                "countryCode3Gid": "US",
                "postalCode": "23237",
                "locationXid": "300000001357157-300000054405994",
                "locationName": "RVA BHI R VIRGINIA IO"
            }
        """
        try:
            # Extract location GID from URL (everything after '/locations/')
            location_gid = location_url.split('/locations/')[-1]
            
            conn = http.client.HTTPSConnection(self.base_url)
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Basic {self.auth_token}'
            }
            
            # Construct the endpoint path
            endpoint_path = f"{self.location_endpoint}/{location_gid}"
            
            conn.request("GET", endpoint_path, headers=headers)
            response = conn.getresponse()
            data = response.read()
            
            if response.status == 200:
                return json.loads(data.decode("utf-8"))
            elif response.status == 404:
                return {"error": "Location not found", "status_code": 404}
            else:
                return {
                    "error": f"Location API request failed with status {response.status}",
                    "status_code": response.status,
                    "response": data.decode("utf-8") if data else None
                }
                
        except Exception as e:
            return {"error": str(e), "status_code": 500}
        finally:
            if 'conn' in locals():
                conn.close()
    
    def get_order_release_locations(self, order_release_gid: str) -> Dict[str, Any]:
        """
        Get consolidated location information for an order release.
        
        Args:
            order_release_gid: The order release GID to fetch locations for
            
        Returns:
            Dictionary containing consolidated location information or error
        """
        try:
            # Step 1: Get order release data
            order_release_result = self.get_order_release(order_release_gid)
            
            if "error" in order_release_result:
                return {
                    "success": False,
                    "order_release_gid": order_release_gid,
                    "error": f"Failed to fetch order release: {order_release_result['error']}",
                    "source_location": None,
                    "destination_location": None,
                    "lane_summary": None
                }
            
            # Step 2: Extract location URLs
            location_urls = self.extract_location_urls(order_release_result)
            
            if not location_urls["source_url"] and not location_urls["dest_url"]:
                return {
                    "success": False,
                    "order_release_gid": order_release_gid,
                    "error": "No location URLs found in order release data",
                    "source_location": None,
                    "destination_location": None,
                    "lane_summary": None
                }
            
            # Step 3: Fetch location details
            source_location_details = None
            dest_location_details = None
            
            if location_urls["source_url"]:
                source_result = self.get_location_details(location_urls["source_url"])
                if "error" not in source_result:
                    source_location_details = source_result
            
            if location_urls["dest_url"]:
                dest_result = self.get_location_details(location_urls["dest_url"])
                if "error" not in dest_result:
                    dest_location_details = dest_result
            
            # Step 4: Build consolidated response
            success = source_location_details is not None or dest_location_details is not None
            
            # Create lane summary if both locations are available
            lane_summary = None
            if source_location_details and dest_location_details:
                source_city_state = f"{source_location_details.get('city', 'Unknown')}, {source_location_details.get('provinceCode', 'Unknown')}"
                dest_city_state = f"{dest_location_details.get('city', 'Unknown')}, {dest_location_details.get('provinceCode', 'Unknown')}"
                
                lane_summary = {
                    "route": f"{source_city_state} to {dest_city_state}",
                    "origin": source_city_state,
                    "destination": dest_city_state
                }
            
            return {
                "success": success,
                "order_release_gid": order_release_gid,
                "source_location": source_location_details,
                "destination_location": dest_location_details,
                "lane_summary": lane_summary,
                "error": None if success else "Failed to retrieve location details"
            }
            
        except Exception as e:
            return {
                "success": False,
                "order_release_gid": order_release_gid,
                "error": f"Unexpected error: {str(e)}",
                "source_location": None,
                "destination_location": None,
                "lane_summary": None
            }
    
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