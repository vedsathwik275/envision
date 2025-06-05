#!/usr/bin/env python3
"""
Test script for RIQ API routes.

This script tests both the REST location API and XML RIQ API by:
1. Getting user input for source and destination cities/states
2. Calling /new-riq-rest to get location IDs
3. Using those IDs to call /riq-xml for rate quotes
4. Parsing and displaying the results
"""

import requests
import json
import sys
from typing import Dict, Any, List
import xml.etree.ElementTree as ET


class RIQAPITester:
    """Test client for RIQ API endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8006"):
        """
        Initialize the tester.
        
        Args:
            base_url: Base URL for the API (default: http://localhost:8006)
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def get_location_ids(self, source_city: str, source_state: str, 
                        dest_city: str, dest_state: str, 
                        source_country: str = "US", dest_country: str = "US") -> Dict[str, Any]:
        """
        Call the /new-riq-rest endpoint to get location IDs.
        
        Args:
            source_city: Source city name
            source_state: Source state code
            dest_city: Destination city name
            dest_state: Destination state code
            source_country: Source country code (default: US)
            dest_country: Destination country code (default: US)
            
        Returns:
            API response dictionary
        """
        url = f"{self.base_url}/new-riq-rest"
        payload = {
            "source_city": source_city,
            "source_state": source_state,
            "source_country": source_country,
            "dest_city": dest_city,
            "dest_state": dest_state,
            "dest_country": dest_country
        }
        
        print(f"\n🔍 Calling REST API to get location IDs...")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"error": f"JSON decode failed: {str(e)}"}
    
    def get_riq_xml_quote(self, source_location_id: str, dest_location_id: str,
                         weight: float, volume: float, 
                         transport_modes: List[str] = None) -> Dict[str, Any]:
        """
        Call the /riq-xml endpoint to get rate quotes.
        
        Args:
            source_location_id: Source location XID
            dest_location_id: Destination location XID
            weight: Weight value
            volume: Volume value
            transport_modes: List of transport modes
            
        Returns:
            API response dictionary
        """
        if transport_modes is None:
            transport_modes = ["LTL", "TL"]
            
        url = f"{self.base_url}/riq-xml"
        payload = {
            "source_location_id": source_location_id,
            "dest_location_id": dest_location_id,
            "weight": weight,
            "volume": volume,
            "weight_unit": "LB",
            "volume_unit": "CUFT",
            "transport_modes": transport_modes,
            "commodity_class": "70.0"
        }
        
        print(f"\n🔍 Calling XML RIQ API to get rate quotes...")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"error": f"JSON decode failed: {str(e)}"}
    
    def display_location_results(self, response: Dict[str, Any]) -> Dict[str, str]:
        """
        Display and extract location IDs from REST API response.
        
        Args:
            response: API response from /new-riq-rest
            
        Returns:
            Dictionary with source_location_id and dest_location_id
        """
        print("\n" + "="*60)
        print("📍 LOCATION ID RESULTS")
        print("="*60)
        
        # if "error" in response:
        #     print(f"❌ Error: {response['error']}")
        #     return {}
        
        if not response.get("success", False):
            print("❌ Request was not successful")
            return {}
        
        locations = response.get("locations", {})
        if not locations:
            print("❌ No locations found")
            return {}
        
        source_id = locations.get("source_location_id")
        dest_id = locations.get("dest_location_id")
        
        print(f"✅ Source Location ID: {source_id}")
        print(f"✅ Destination Location ID: {dest_id}")
        
        # Display raw response count
        raw_response = response.get("raw_response", {})
        item_count = len(raw_response.get("items", []))
        print(f"📊 Total locations found in database: {item_count}")
        
        return {
            "source_location_id": source_id,
            "dest_location_id": dest_id
        }
    
    def parse_xml_response(self, xml_string: str) -> List[Dict[str, Any]]:
        """
        Parse the XML response to extract RIQ results.
        
        Args:
            xml_string: Raw XML response string
            
        Returns:
            List of parsed result dictionaries
        """
        try:
            # Parse the XML
            root = ET.fromstring(xml_string)
            
            # Define namespace
            ns = {'otm': 'http://xmlns.oracle.com/apps/otm/transmission/v6.4'}
            
            # Find all RIQ results
            results = []
            riq_results = root.findall('.//otm:RIQResult', ns)
            
            for riq_result in riq_results:
                result = {}
                
                # Service Provider (Carrier)
                sp_elem = riq_result.find('otm:ServiceProviderGid/otm:Gid/otm:Xid', ns)
                result['service_provider'] = sp_elem.text if sp_elem is not None else 'Unknown'
                
                # Transport Mode
                tm_elem = riq_result.find('otm:TransportModeGid/otm:Gid/otm:Xid', ns)
                result['transport_mode'] = tm_elem.text if tm_elem is not None else 'Unknown'
                
                # Cost
                cost_elem = riq_result.find('otm:Cost/otm:FinancialAmount/otm:MonetaryAmount', ns)
                if cost_elem is not None:
                    try:
                        result['cost'] = float(cost_elem.text)
                    except (ValueError, TypeError):
                        result['cost'] = None
                else:
                    result['cost'] = None
                
                # Currency
                currency_elem = riq_result.find('otm:Cost/otm:FinancialAmount/otm:GlobalCurrencyCode', ns)
                result['currency'] = currency_elem.text if currency_elem is not None else 'USD'
                
                # Distance
                dist_elem = riq_result.find('otm:Distance/otm:DistanceValue', ns)
                if dist_elem is not None:
                    try:
                        result['distance'] = float(dist_elem.text)
                    except (ValueError, TypeError):
                        result['distance'] = None
                else:
                    result['distance'] = None
                
                # Distance unit
                dist_unit_elem = riq_result.find('otm:Distance/otm:DistanceUOMGid/otm:Gid/otm:Xid', ns)
                result['distance_unit'] = dist_unit_elem.text if dist_unit_elem is not None else 'MI'
                
                # Transit Time
                transit_elem = riq_result.find('otm:TransitTime/otm:Duration/otm:DurationValue', ns)
                if transit_elem is not None:
                    try:
                        result['transit_time_hours'] = float(transit_elem.text)
                    except (ValueError, TypeError):
                        result['transit_time_hours'] = None
                else:
                    result['transit_time_hours'] = None
                
                # Transit time unit
                transit_unit_elem = riq_result.find('otm:TransitTime/otm:Duration/otm:DurationUOMGid/otm:Gid/otm:Xid', ns)
                result['transit_time_unit'] = transit_unit_elem.text if transit_unit_elem is not None else 'H'
                
                # Is Optimal
                optimal_elem = riq_result.find('otm:IsOptimalResult', ns)
                result['is_optimal'] = optimal_elem.text == 'Y' if optimal_elem is not None else False
                
                results.append(result)
            
            return results
            
        except ET.ParseError as e:
            print(f"❌ XML Parse Error: {str(e)}")
            return []
        except Exception as e:
            print(f"❌ Error parsing XML: {str(e)}")
            return []
    
    def display_riq_results(self, response: Dict[str, Any]) -> None:
        """
        Display and parse RIQ XML API response.
        
        Args:
            response: API response from /riq-xml
        """
        print("\n" + "="*60)
        print("🚛 RIQ RATE QUOTE RESULTS")
        print("="*60)
        
        # if "error" in response:
        #     print(f"❌ Error: {response['error']}")
        #     return
        
        if not response.get("success", False):
            print("❌ Request was not successful")
            if "error" in response and response["error"]:
                print(f"Error details: {response['error']}")
            return
        
        # Print raw XML for debugging
        raw_xml_request = response.get("raw_xml_request", "")
        raw_xml_response = response.get("raw_xml_response", "")
        
        if raw_xml_request:
            print("\n🔍 RAW XML REQUEST:")
            print("-" * 50)
            print(raw_xml_request[:500] + "..." if len(raw_xml_request) > 500 else raw_xml_request)
        
        if raw_xml_response:
            print("\n🔍 RAW XML RESPONSE:")
            print("-" * 50)
            print(raw_xml_response[:500] + "..." if len(raw_xml_response) > 500 else raw_xml_response)
        
        # Parse the XML response
        if not raw_xml_response:
            print("❌ No XML response to parse")
            return
            
        results = self.parse_xml_response(raw_xml_response)
        
        if not results:
            print("❌ No rate quotes found in XML response")
            return
        
        print(f"\n✅ Found {len(results)} rate option(s)\n")
        
        # Group results by carrier for better display
        carriers = {}
        for i, result in enumerate(results, 1):
            carrier = result.get("service_provider", "Unknown Carrier")
            if carrier not in carriers:
                carriers[carrier] = []
            carriers[carrier].append((i, result))
        
        # Display results grouped by carrier
        for carrier, carrier_results in carriers.items():
            print(f"🏢 CARRIER: {carrier}")
            print("-" * 50)
            
            for result_num, result in carrier_results:
                print(f"  Option #{result_num}:")
                print(f"    🚛 Transport Mode: {result.get('transport_mode', 'N/A')}")
                
                cost = result.get('cost')
                cost_str = f"${cost:.2f}" if cost is not None else "N/A"
                print(f"    💰 Cost: {cost_str} {result.get('currency', 'USD')}")
                
                distance = result.get('distance')
                distance_str = f"{distance:.1f}" if distance is not None else "N/A"
                print(f"    📏 Distance: {distance_str} {result.get('distance_unit', 'MI')}")
                
                transit = result.get('transit_time_hours')
                transit_str = f"{transit:.1f}" if transit is not None else "N/A"
                print(f"    ⏱️  Transit Time: {transit_str} {result.get('transit_time_unit', 'hours')}")
                
                is_optimal = result.get('is_optimal', False)
                optimal_text = "✨ CHEAPEST OPTION" if is_optimal else "Standard Option"
                print(f"    🎯 Status: {optimal_text}")
                print()
        
        # Summary statistics
        print("📊 SUMMARY STATISTICS")
        print("-" * 50)
        costs = [r.get('cost') for r in results if r.get('cost') is not None]
        if costs:
            print(f"💰 Price Range: ${min(costs):.2f} - ${max(costs):.2f}")
            print(f"💰 Average Cost: ${sum(costs)/len(costs):.2f}")
        
        distances = [r.get('distance') for r in results if r.get('distance') is not None]
        if distances:
            print(f"📏 Distance Range: {min(distances):.1f} - {max(distances):.1f} miles")
        
        transit_times = [r.get('transit_time_hours') for r in results if r.get('transit_time_hours') is not None]
        if transit_times:
            print(f"⏱️  Transit Time Range: {min(transit_times):.1f} - {max(transit_times):.1f} hours")
        
        # Show optimal options
        optimal_options = [r for r in results if r.get('is_optimal', False)]
        if optimal_options:
            print(f"\n✨ OPTIMAL OPTIONS ({len(optimal_options)}):")
            for opt in optimal_options:
                cost = opt.get('cost')
                cost_str = f"${cost:.2f}" if cost is not None else "N/A"
                transit = opt.get('transit_time_hours')
                transit_str = f"{transit:.1f}" if transit is not None else "N/A"
                print(f"  • {opt.get('service_provider', 'Unknown')} - "
                      f"{opt.get('transport_mode', 'N/A')} - "
                      f"{cost_str} - "
                      f"{transit_str} hours")
        
        print(f"\n🏢 UNIQUE CARRIERS ({len(carriers)}):")
        for carrier in carriers.keys():
            print(f"  • {carrier}")


def get_user_input() -> Dict[str, str]:
    """
    Get lane information from user input.
    
    Returns:
        Dictionary with source and destination information
    """
    print("🚛 RIQ API Tester")
    print("="*50)
    print("Enter lane information to test both API endpoints\n")
    
    # Get source information
    print("📍 SOURCE LOCATION:")
    source_city = input("  Enter source city: ").strip()
    source_state = input("  Enter source state (e.g., TX, CA): ").strip().upper()
    
    print("\n📍 DESTINATION LOCATION:")
    dest_city = input("  Enter destination city: ").strip()
    dest_state = input("  Enter destination state (e.g., TX, CA): ").strip().upper()
    
    return {
        "source_city": source_city,
        "source_state": source_state,
        "dest_city": dest_city,
        "dest_state": dest_state
    }


def main():
    """Main function to run the test."""
    try:
        # Get user input
        lane_info = get_user_input()
        
        # Validate input
        required_fields = ["source_city", "source_state", "dest_city", "dest_state"]
        if not all(lane_info.get(field) for field in required_fields):
            print("❌ Error: All fields are required")
            return
        
        # Initialize tester
        tester = RIQAPITester()
        
        # Step 1: Get location IDs
        location_response = tester.get_location_ids(
            lane_info["source_city"],
            lane_info["source_state"],
            lane_info["dest_city"],
            lane_info["dest_state"]
        )
        
        # Display and extract location results
        location_ids = tester.display_location_results(location_response)
        
        if not location_ids.get("source_location_id") or not location_ids.get("dest_location_id"):
            print("❌ Cannot proceed without both location IDs")
            return
        
        # Step 2: Get RIQ quotes using location IDs
        riq_response = tester.get_riq_xml_quote(
            location_ids["source_location_id"],
            location_ids["dest_location_id"],
            weight=2400,  # Default weight
            volume=15     # Default volume
        )
        
        # Display RIQ results
        tester.display_riq_results(riq_response)
        
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 