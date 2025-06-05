"""
Test script for AI Transportation Recommendations system.

This script tests the core functionality of the recommendation service
to ensure it's working correctly with sample data.
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the api directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from api.models import RecommendationRequest
from api.services.recommendation_service import AITransportationRecommendationService


async def test_recommendation_service():
    """Test the AI Transportation Recommendation Service with sample data."""
    
    print("🧪 Testing AI Transportation Recommendation Service...")
    
    # Initialize the service
    service = AITransportationRecommendationService()
    
    # Sample aggregated data
    sample_data = {
        "riq_data": {
            "lane_info": {
                "sourceCity": "Los Angeles",
                "destinationCity": "Chicago",
                "bestCarrier": "ODFL",
                "bestPerformance": "92.5%"
            },
            "user_message": "What are the rates from Los Angeles to Chicago?",
            "timestamp": datetime.now().isoformat()
        },
        "spot_data": {
            "origin_city": "Los Angeles",
            "destination_city": "Chicago",
            "spot_costs": [
                {
                    "carrier": "ODFL",
                    "cost_details": [
                        {"total_spot_cost": "2450.00", "transport_mode": "LTL"}
                    ]
                },
                {
                    "carrier": "YRC",
                    "cost_details": [
                        {"total_spot_cost": "2380.00", "transport_mode": "LTL"}
                    ]
                }
            ]
        },
        "historical_data": {
            "cost_statistics": {
                "avg_cost_per_mile": 1.85,
                "avg_cost_per_lb": 0.12
            },
            "lane_summary": {
                "most_common_mode": "LTL",
                "route": "Los Angeles to Chicago"
            },
            "total_count": 150
        },
        "chat_insights": {
            "best_performer": {
                "carrier": "ODFL",
                "performance": "92.5%"
            },
            "worst_performer": {
                "carrier": "XPO",
                "performance": "78.2%"
            }
        }
    }
    
    # Create test request
    request = RecommendationRequest(
        aggregated_data=sample_data,
        source_city="Los Angeles",
        destination_city="Chicago",
        weight="15000 lbs",
        volume="750 cuft",
        context="Test transportation lane analysis"
    )
    
    try:
        print("📊 Generating AI recommendation...")
        
        # Generate recommendation
        recommendation = await service.generate_recommendation(request)
        
        print("✅ Recommendation generated successfully!")
        print(f"📈 Confidence Score: {recommendation.confidence_score:.2%}")
        print(f"🎯 Primary Recommendation: {recommendation.primary_recommendation[:200]}...")
        print(f"🚛 Recommended Carrier: {recommendation.recommended_carrier}")
        print(f"💰 Strategy: {recommendation.cost_optimization.strategy_type}")
        print(f"⚠️  Risk Level: {recommendation.risk_assessment.overall_risk_level}")
        print(f"📅 Market Timing: {recommendation.market_timing[:100]}...")
        print(f"🔍 Data Sources Used: {', '.join(recommendation.metadata.data_sources_used)}")
        print(f"📊 Data Completeness: {recommendation.metadata.data_completeness:.1%}")
        
        if recommendation.alternatives:
            print(f"🔄 Alternatives: {len(recommendation.alternatives)} options provided")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False


async def test_data_validation():
    """Test the data validation functionality."""
    
    print("\n🔍 Testing data validation...")
    
    try:
        from api.routes.recommendations import validate_aggregated_data
        
        # Test with complete data
        complete_data = {
            "riq_data": {"test": "data"},
            "spot_data": {"test": "data"},
            "historical_data": {"test": "data"},
            "chat_insights": {"test": "data"},
            "order_data": {"test": "data"}
        }
        
        validation_result = await validate_aggregated_data(complete_data)
        print(f"✅ Complete data validation: {validation_result['data_completeness']:.1%} complete")
        
        # Test with partial data
        partial_data = {
            "riq_data": {"test": "data"},
            "spot_data": {"test": "data"}
        }
        
        validation_result = await validate_aggregated_data(partial_data)
        print(f"🟡 Partial data validation: {validation_result['data_completeness']:.1%} complete")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation test failed: {str(e)}")
        return False


async def main():
    """Run all tests."""
    
    print("🚀 Starting AI Transportation Recommendations System Tests\n")
    
    # Check environment
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
        print("   Set your OpenAI API key to test the full functionality")
        return
    
    print(f"🔑 OpenAI API Key: {'*' * (len(openai_key) - 8) + openai_key[-8:]}")
    
    # Run tests
    tests = [
        ("AI Recommendation Service", test_recommendation_service),
        ("Data Validation", test_data_validation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        result = await test_func()
        results.append((test_name, result))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The AI Transportation Recommendations system is ready.")
    else:
        print("⚠️  Some tests failed. Please check the configuration and try again.")


if __name__ == "__main__":
    asyncio.run(main()) 