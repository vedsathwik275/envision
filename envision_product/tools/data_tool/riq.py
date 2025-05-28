import http.client
import json
import os
from typing import Optional, Dict, Any


class RIQClient:
    """Oracle Transportation Management RIQ (Rate, Inventory, Quote) API client."""
    
    def __init__(self, base_url: str, auth_token: str) -> None:
        """
        Initialize RIQ client.
        
        Args:
            base_url: Base URL for the RIQ API
            auth_token: Authentication token for API access
        """
        self.base_url = base_url
        self.auth_token = auth_token
        self.endpoint = "/logisticsRestApi/resources-int/v2/custom-actions/riqRateAndRoute"
    
    def create_location(self, city: str, province_code: str, postal_code: str, country_code: str = "US") -> Dict[str, str]:
        """
        Create a location object for RIQ request.
        
        Args:
            city: City name
            province_code: State or province code
            postal_code: Postal or ZIP code
            country_code: Country code (default: "US")
            
        Returns:
            Dictionary containing location information
        """
        return {
            "city": city,
            "provinceCode": province_code,
            "postalCode": postal_code,
            "countryCode3Gid": country_code
        }
    
    def create_item(self, weight_value: float, weight_unit: str = "LB", 
                   volume_value: float = 0, volume_unit: str = "CUFT",
                   declared_value: float = 0, currency: str = "USD",
                   package_count: int = 1, packaged_item_gid: str = "DEFAULT") -> Dict[str, Any]:
        """
        Create an item object for RIQ request.
        
        Args:
            weight_value: Weight of the item
            weight_unit: Unit of weight measurement (default: "LB")
            volume_value: Volume of the item (default: 0)
            volume_unit: Unit of volume measurement (default: "CUFT")
            declared_value: Declared value of the item (default: 0)
            currency: Currency for declared value (default: "USD")
            package_count: Number of packages (default: 1)
            packaged_item_gid: Packaged item GID (default: "DEFAULT")
            
        Returns:
            Dictionary containing item information
        """
        return {
            "packagedItemGid": packaged_item_gid,
            "weight": {
                "value": weight_value,
                "unit": weight_unit
            },
            "volume": {
                "value": volume_value,
                "unit": volume_unit
            },
            "declaredValue": {
                "value": declared_value,
                "currency": currency
            },
            "itemPackageCount": package_count
        }
    
    def create_rate_request(self, source_location: Dict[str, str], destination_location: Dict[str, str],
                           items: list, servprov_gid: str = "BSL.RYGB",
                           request_type: str = "AllOptions", perspective: str = "B",
                           max_primary_options: str = "99", 
                           primary_option_definition: str = "BY_ITINERARY") -> Dict[str, Any]:
        """
        Create a complete RIQ rate request payload.
        
        Args:
            source_location: Source location dictionary
            destination_location: Destination location dictionary
            items: List of items to ship
            servprov_gid: Service provider GID (default: "BSL.RYGB")
            request_type: Type of request (default: "AllOptions")
            perspective: Request perspective (default: "B")
            max_primary_options: Maximum primary options (default: "99")
            primary_option_definition: Primary option definition (default: "BY_ITINERARY")
            
        Returns:
            Dictionary containing complete rate request payload
        """
        return {
            "requestType": request_type,
            "perspective": perspective,
            "maxPrimaryOptions": max_primary_options,
            "primaryOptionDefinition": primary_option_definition,
            "orderReleases": {
                "sourceLocation": source_location,
                "destinationLocation": destination_location,
                "servprovGid": servprov_gid,
                "lines": {
                    "items": items
                }
            }
        }
    
    def get_rate_quote(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send RIQ rate request and return parsed response.
        
        Args:
            request_payload: Complete rate request payload
            
        Returns:
            Dictionary containing API response or error information
        """
        conn = http.client.HTTPSConnection(self.base_url)
        
        headers = {
            'Content-Type': 'application/vnd.oracle.resource+json;type=query-def',
            'Prefer': 'transient',
            'Authorization': f'Basic {self.auth_token}'
        }
        
        payload_json = json.dumps(request_payload)
        
        try:
            conn.request("POST", self.endpoint, payload_json, headers)
            response = conn.getresponse()
            data = response.read()
            return json.loads(data.decode("utf-8"))
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()


def main() -> None:
    """Example usage of RIQClient."""
    # Configuration
    BASE_URL = "otmgtm-test-ejhu.otmgtm.us-ashburn-1.ocs.oraclecloud.com"
    AUTH_TOKEN = "QlNMLkNIUl9JTlRFR1JBVElPTjpyNWgzRDFiQ21WMWxmUmQ4cUBpNHpnNiZJ"
    
    # Initialize client
    client = RIQClient(BASE_URL, AUTH_TOKEN)
    
    # Create locations
    source = client.create_location("LANCASTER", "TX", "75134")
    destination = client.create_location("OWASSO", "OK", "74055")
    
    # Create items
    items = [client.create_item(weight_value=2400, volume_value=150)]
    
    # Create request
    request_payload = client.create_rate_request(source, destination, items)
    
    # Get rate quote
    result = client.get_rate_quote(request_payload)
    
    # Print result
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()