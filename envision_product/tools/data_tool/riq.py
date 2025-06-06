import http.client
import json
import os
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import uuid
from datetime import datetime

import ssl
ssl._create_default_https_context = ssl._create_unverified_context
# only do the above if you are using the mac

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
        self.locations_endpoint = "/logisticsRestApi/resources-int/v2/custom-actions/queries/locations"
        self.xml_endpoint = "/GC3/glog.integration.servlet.WMServlet"
    
    def create_location(self, city: str, province_code: str, postal_code: str = "00000", country_code: str = "US") -> Dict[str, str]:
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
                           items: list, servprov_gid: Optional[str] = "BSL.RYGB",
                           request_type: str = "AllOptions", perspective: str = "B",
                           max_primary_options: str = "99", 
                           primary_option_definition: str = "BY_ITINERARY") -> Dict[str, Any]:
        """
        Create a complete RIQ rate request payload.
        
        Args:
            source_location: Source location dictionary
            destination_location: Destination location dictionary
            items: List of items to ship
            servprov_gid: Service provider GID (optional, default: "BSL.RYGB")
            request_type: Type of request (default: "AllOptions")
            perspective: Request perspective (default: "B")
            max_primary_options: Maximum primary options (default: "99")
            primary_option_definition: Primary option definition (default: "BY_ITINERARY")
            
        Returns:
            Dictionary containing complete rate request payload
        """
        order_releases = {
            "sourceLocation": source_location,
            "destinationLocation": destination_location,
            "lines": {
                "items": items
            }
        }
        
        # Only include servprov_gid if it's provided (not None)
        if servprov_gid is not None:
            order_releases["servprovGid"] = servprov_gid
        
        return {
            "requestType": request_type,
            "perspective": perspective,
            "maxPrimaryOptions": max_primary_options,
            "primaryOptionDefinition": primary_option_definition,
            "orderReleases": order_releases
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

    def get_location_ids(self, source_city: str, source_state: str, source_country: str,
                        dest_city: str, dest_state: str, dest_country: str) -> Dict[str, Any]:
        """
        Query Oracle's REST API to get location IDs for a given lane.
        
        Args:
            source_city: Source city name
            source_state: Source state/province code
            source_country: Source country code
            dest_city: Destination city name
            dest_state: Destination state/province code
            dest_country: Destination country code
            
        Returns:
            Dictionary containing location IDs or error information
        """
        conn = http.client.HTTPSConnection(self.base_url)
        
        headers = {
            'Content-Type': 'application/vnd.oracle.resource+json;type=query-def',
            'Prefer': 'transient',
            'Authorization': f'Basic {self.auth_token}'
        }
        
        # Create POST payload for locations query
        query_payload = {
            "copiedFrom": "BSL.LOCATIONS_BY_LANE",
            "parameterValues": {
                "0": source_city,
                "1": source_state,
                "2": source_country,
                "3": dest_city,
                "4": dest_state,
                "5": dest_country
            }
        }
        
        payload_json = json.dumps(query_payload)
        
        try:
            # Use POST request with JSON payload
            conn.request("POST", self.locations_endpoint, payload_json, headers)
            response = conn.getresponse()
            
            if response.status != 200:
                return {"error": f"HTTP {response.status}: {response.reason}"}
            
            data = response.read()
            response_data = json.loads(data.decode("utf-8"))
            
            # Extract location IDs from response
            locations = {}
            if "items" in response_data:
                for item in response_data["items"]:
                    city = item.get("city", "").upper()
                    state = item.get("provinceCode", "").upper()
                    country = item.get("countryCode3Gid", "").upper()
                    location_xid = item.get("locationXid")
                    
                    # Match source location
                    if (source_city.upper() in city and 
                        source_state.upper() == state and 
                        source_country.upper() == country):
                        locations["source_location_id"] = location_xid
                    
                    # Match destination location
                    if (dest_city.upper() in city and 
                        dest_state.upper() == state and 
                        dest_country.upper() == country):
                        locations["dest_location_id"] = location_xid
            
            return {
                "success": True,
                "locations": locations,
                "raw_response": response_data
            }
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()

    def generate_xml_request(self, source_location_id: str, dest_location_id: str,
                           weight: float, volume: float = 0, 
                           transport_modes: List[str] = None) -> str:
        """
        Generate XML request for RIQ query.
        
        Args:
            source_location_id: Source location XID
            dest_location_id: Destination location XID
            weight: Weight value
            volume: Volume value (optional)
            transport_modes: List of transport modes (optional, defaults to ['LTL', 'TL'])
            
        Returns:
            XML string for RIQ request
        """
        if transport_modes is None:
            transport_modes = ['LTL', 'TL']
        
        # Generate unique transmission number
        transmission_no = f"{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8]}"
        
        # Start building XML with correct namespace and structure
        xml_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<Transmission xmlns="http://xmlns.oracle.com/apps/otm/transmission/v6.4">',
            '	<TransmissionHeader>',
            '		<TransmissionType>QUERY</TransmissionType>',
            f'		<SenderTransmissionNo>{transmission_no}</SenderTransmissionNo>',
            '	</TransmissionHeader>',
            '	<TransmissionBody>',
            '		<GLogXMLElement>',
            '			<RemoteQuery>',
            '				<RIQQuery>',
            '					<RIQRequestType>AllOptions</RIQRequestType>',
            '					<SourceAddress>',
            '						<MileageAddress>',
            '							<LocationGid>',
            '								<Gid>',
            '									<DomainName>BSL</DomainName>',
            f'									<Xid>{source_location_id}</Xid>',
            '								</Gid>',
            '							</LocationGid>',
            '						</MileageAddress>',
            '					</SourceAddress>',
            '					<DestAddress>',
            '						<MileageAddress>',
            '							<LocationGid>',
            '								<Gid>',
            '									<DomainName>BSL</DomainName>',
            f'									<Xid>{dest_location_id}</Xid>',
            '								</Gid>',
            '							</LocationGid>',
            '						</MileageAddress>',
            '					</DestAddress>'
        ]
        
        # Add transport modes
        for mode in transport_modes:
            xml_parts.extend([
                '					<TransportModeGid>',
                '						<Gid>',
                f'							<Xid>{mode}</Xid>',
                '						</Gid>',
                '					</TransportModeGid>'
            ])
        
        # Add ship unit with weight and volume
        xml_parts.extend([
            '					<ShipUnit>',
            '						<WeightVolume>',
            '							<Weight>',
            f'								<WeightValue>{weight}</WeightValue>',
            '								<WeightUOMGid>',
            '									<Gid>',
            '										<Xid>LB</Xid>',
            '									</Gid>',
            '								</WeightUOMGid>',
            '							</Weight>'
        ])
        
        # Add volume if provided
        if volume > 0:
            xml_parts.extend([
                '							<Volume>',
                f'								<VolumeValue>{volume}</VolumeValue>',
                '								<VolumeUOMGid>',
                '									<Gid>',
                '										<Xid>CUFT</Xid>',
                '									</Gid>',
                '								</VolumeUOMGid>',
                '							</Volume>'
            ])
        
        # Close WeightVolume and add commodity classification
        xml_parts.extend([
            '						</WeightVolume>',
            '						<FlexCommodityQualifierGid>',
            '							<Gid>',
            '								<Xid>NMFC_CLASS</Xid>',
            '							</Gid>',
            '						</FlexCommodityQualifierGid>',
            '						<FlexCommodityValue>70.0</FlexCommodityValue>',
            '						<ShipUnitCount>1</ShipUnitCount>',
            '					</ShipUnit>',
            '				</RIQQuery>',
            '			</RemoteQuery>',
            '		</GLogXMLElement>',
            '	</TransmissionBody>',
            '</Transmission>'
        ])
        
        return '\n'.join(xml_parts)

    def parse_xml_response(self, xml_response: str) -> Dict[str, Any]:
        """
        Parse XML response from RIQ query.
        
        Args:
            xml_response: XML response string from Oracle
            
        Returns:
            Dictionary containing parsed response data
        """
        try:
            # Parse XML with namespace handling
            root = ET.fromstring(xml_response)
            
            # Define namespace - Oracle uses this namespace in responses
            namespaces = {'otm': 'http://xmlns.oracle.com/apps/otm'}
            
            # Check for errors first
            stack_trace = root.find('.//otm:StackTrace', namespaces)
            if stack_trace is not None:
                return {"error": f"Oracle API Error: {stack_trace.text}"}
            
            # Extract RIQ results from RemoteQueryReply
            results = []
            riq_results = root.findall('.//otm:RemoteQueryReply/otm:RIQQueryReply/otm:RIQResult', namespaces)
            
            for result in riq_results:
                parsed_result = {}
                
                # Service Provider
                service_provider = result.find('.//otm:ServiceProviderGid/otm:Gid/otm:Xid', namespaces)
                if service_provider is not None:
                    parsed_result['service_provider'] = service_provider.text
                
                # Transport Mode
                transport_mode = result.find('.//otm:TransportModeGid/otm:Gid/otm:Xid', namespaces)
                if transport_mode is not None:
                    parsed_result['transport_mode'] = transport_mode.text
                
                # Cost
                cost_element = result.find('.//otm:Cost/otm:FinancialAmount/otm:MonetaryAmount', namespaces)
                if cost_element is not None:
                    parsed_result['cost'] = float(cost_element.text)
                
                # Currency
                currency_element = result.find('.//otm:Cost/otm:FinancialAmount/otm:CurrencyGid/otm:Gid/otm:Xid', namespaces)
                if currency_element is not None:
                    parsed_result['currency'] = currency_element.text
                
                # Distance
                distance_element = result.find('.//otm:Distance/otm:DistanceValue', namespaces)
                if distance_element is not None:
                    parsed_result['distance'] = float(distance_element.text)
                
                # Distance Unit
                distance_unit = result.find('.//otm:Distance/otm:DistanceUom/otm:Gid/otm:Xid', namespaces)
                if distance_unit is not None:
                    parsed_result['distance_unit'] = distance_unit.text
                
                # Is Optimal Result
                is_optimal = result.find('.//otm:IsOptimalResult', namespaces)
                if is_optimal is not None:
                    parsed_result['is_optimal'] = is_optimal.text.lower() == 'true'
                
                # Transit Time
                transit_time = result.find('.//otm:TransitTime/otm:Duration/otm:DurationValue', namespaces)
                if transit_time is not None:
                    parsed_result['transit_time_hours'] = float(transit_time.text)
                
                # Transit Time Unit
                transit_time_unit = result.find('.//otm:TransitTime/otm:Duration/otm:DurationUom/otm:Gid/otm:Xid', namespaces)
                if transit_time_unit is not None:
                    parsed_result['transit_time_unit'] = transit_time_unit.text
                
                if parsed_result:  # Only add if we found some data
                    results.append(parsed_result)
            
            return {
                "success": True,
                "results": results,
                "total_results": len(results)
            }
            
        except ET.ParseError as e:
            return {"error": f"XML parsing error: {str(e)}"}
        except Exception as e:
            return {"error": f"Error parsing XML response: {str(e)}"}

    def get_riq_xml_quote(self, source_location_id: str, dest_location_id: str,
                         weight: float, volume: float = 0, 
                         transport_modes: List[str] = None) -> Dict[str, Any]:
        """
        Get RIQ quote using XML API.
        
        Args:
            source_location_id: Source location XID
            dest_location_id: Destination location XID
            weight: Weight value
            volume: Volume value (optional)
            transport_modes: List of transport modes (optional)
            
        Returns:
            Dictionary containing parsed RIQ response or error information
        """
        conn = http.client.HTTPSConnection(self.base_url)
        
        headers = {
            'Content-Type': 'application/xml',
            'Authorization': f'Basic {self.auth_token}'
        }
        
        # Generate XML request
        xml_request = self.generate_xml_request(
            source_location_id, dest_location_id, weight, volume, transport_modes
        )
        
        try:
            conn.request("POST", self.xml_endpoint, xml_request, headers)
            response = conn.getresponse()
            
            if response.status != 200:
                return {"error": f"HTTP {response.status}: {response.reason}"}
            
            xml_response = response.read().decode("utf-8")
            
            # Parse the XML response
            parsed_response = self.parse_xml_response(xml_response)
            
            # Add raw XML for debugging if needed
            parsed_response["raw_xml_request"] = xml_request
            parsed_response["raw_xml_response"] = xml_response
            
            return parsed_response
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()


def main() -> None:
    """
    Example usage of RIQClient.

    Reads configuration from environment variables, initializes the client,
    creates sample locations and items, generates a rate request payload,
    gets a rate quote, and prints the result.
    """
    # Load environment variables from .env file in data_tool directory
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    # Configuration
    BASE_URL = os.environ.get("BASE_URL")
    AUTH_TOKEN = os.environ.get("AUTH_TOKEN")

    if not BASE_URL or not AUTH_TOKEN:
        print("Error: RIQ_BASE_URL and RIQ_AUTH_TOKEN environment variables must be set.")
        return

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