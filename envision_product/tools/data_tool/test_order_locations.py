"""
Test script for Order Release Location Consolidation feature.

This script tests the new endpoint `/order-release/{order_release_gid}/locations`
and validates the consolidated location information functionality.
"""

import requests
import json
from typing import Dict, Any

def test_order_release_locations() -> None:
    """Test the new order release locations functionality."""
    
    # Configuration - modify as needed
    base_url = "http://localhost:8006"  # Adjust to your server URL
    test_order_release_gid = "BSL.313736"  # Known test GID
    
    print(f"Testing Order Release Location Consolidation")
    print(f"Server: {base_url}")
    print(f"Test Order Release GID: {test_order_release_gid}")
    print("-" * 60)
    
    # Test 1: Valid order release GID
    print("\n1. Testing with valid order release GID...")
    try:
        response = requests.get(f"{base_url}/order-release/{test_order_release_gid}/locations")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Response received:")
            print(f"   Success: {data.get('success')}")
            print(f"   Order Release GID: {data.get('order_release_gid')}")
            
            # Check source location
            source_loc = data.get('source_location')
            if source_loc:
                print(f"   Source Location:")
                print(f"     City: {source_loc.get('city')}")
                print(f"     Province: {source_loc.get('province_code')}")
                print(f"     Country: {source_loc.get('country_code')}")
                print(f"     Location XID: {source_loc.get('location_xid')}")
            else:
                print("   Source Location: Not found")
            
            # Check destination location
            dest_loc = data.get('destination_location')
            if dest_loc:
                print(f"   Destination Location:")
                print(f"     City: {dest_loc.get('city')}")
                print(f"     Province: {dest_loc.get('province_code')}")
                print(f"     Country: {dest_loc.get('country_code')}")
                print(f"     Location XID: {dest_loc.get('location_xid')}")
            else:
                print("   Destination Location: Not found")
            
            # Check lane summary
            lane_summary = data.get('lane_summary')
            if lane_summary:
                print(f"   Lane Summary:")
                print(f"     Route: {lane_summary.get('route')}")
                print(f"     Origin: {lane_summary.get('origin')}")
                print(f"     Destination: {lane_summary.get('destination')}")
            else:
                print("   Lane Summary: Not available")
            
            # Check for errors
            if data.get('error'):
                print(f"   Error: {data.get('error')}")
                
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 2: Invalid order release GID
    print("\n2. Testing with invalid order release GID...")
    invalid_gid = "INVALID.123"
    try:
        response = requests.get(f"{base_url}/order-release/{invalid_gid}/locations")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 404:
            print("✅ Correctly returned 404 for invalid GID")
            error_data = response.json()
            print(f"   Error Detail: {error_data.get('detail')}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 3: Health check to ensure service is running
    print("\n3. Testing service health...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health Check Status: {response.status_code}")
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Service is healthy: {health_data.get('status')}")
        else:
            print(f"❌ Service health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("Note: Ensure the FastAPI server is running on the specified URL")
    print("      and that you have valid Oracle API credentials configured.")

def test_local_service_methods() -> None:
    """Test the service methods directly (if running locally)."""
    
    try:
        import os
        from dotenv import load_dotenv
        from order_release_service import OrderReleaseService
        
        # Load environment variables
        load_dotenv()
        base_url = os.getenv("BASE_URL")
        auth_token = os.getenv("AUTH_TOKEN")
        
        if not base_url or not auth_token:
            print("❌ BASE_URL or AUTH_TOKEN not configured in environment")
            return
        
        print("\nTesting OrderReleaseService methods directly...")
        print("-" * 50)
        
        # Initialize service
        service = OrderReleaseService(base_url, auth_token)
        
        # Test with known order release GID
        test_gid = "BSL.313736"
        
        print(f"\nTesting get_order_release_locations('{test_gid}')...")
        result = service.get_order_release_locations(test_gid)
        
        print(f"Success: {result.get('success')}")
        print(f"Order Release GID: {result.get('order_release_gid')}")
        
        if result.get('error'):
            print(f"Error: {result.get('error')}")
        else:
            print("✅ Method executed successfully")
            
            # Print location details if available
            if result.get('source_location'):
                source = result['source_location']
                print(f"Source: {source.get('city')}, {source.get('provinceCode')}")
            
            if result.get('destination_location'):
                dest = result['destination_location']
                print(f"Destination: {dest.get('city')}, {dest.get('provinceCode')}")
        
    except ImportError:
        print("❌ Cannot import local modules. Run this from the project directory.")
    except Exception as e:
        print(f"❌ Local testing failed: {e}")

if __name__ == "__main__":
    print("Order Release Location Consolidation - Test Suite")
    print("=" * 60)
    
    # Test the API endpoints
    test_order_release_locations()
    
    # Test local service methods if possible
    test_local_service_methods() 