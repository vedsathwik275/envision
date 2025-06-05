"""
Routes for AI Transportation Recommendations.

This module provides endpoints for generating intelligent transportation recommendations
using the enhanced RAG chain model configuration and prompting techniques.
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse

from ..models import (
    RecommendationRequest, 
    RecommendationResponse, 
    ErrorResponse
)
from ..services.recommendation_service import AITransportationRecommendationService
from ..core.exceptions import RAGChatbotException

router = APIRouter(
    prefix="/recommendations",
    tags=["Transportation Recommendations"],
    responses={
        404: {"model": ErrorResponse, "description": "Not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)

logger = logging.getLogger(__name__)

# Dependency to get the recommendation service
def get_recommendation_service() -> AITransportationRecommendationService:
    """
    Dependency to get the AI Transportation Recommendation Service instance.
    
    Returns:
        AITransportationRecommendationService: Service instance for generating recommendations
    """
    return AITransportationRecommendationService()


@router.post(
    "/generate",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate AI Transportation Recommendations",
    description="""
    Generate intelligent transportation recommendations based on aggregated market data.
    
    This endpoint uses the same proven model configuration (gpt-4o-mini with temperature 0.7)
    and sophisticated prompting techniques from the enhanced RAG chain to analyze:
    - RIQ rate quotes and comparisons
    - Spot rate matrix with carrier performance
    - Historical lane statistics and trends
    - Chat-parsed insights (best/worst performers)
    - Order release data
    
    The AI analyzes all available data to provide:
    - Primary recommendation with detailed reasoning
    - Cost optimization analysis (RIQ vs spot rate strategies)
    - Risk assessment based on performance metrics
    - Alternative options and market timing
    - Confidence scoring and data completeness assessment
    """
)
async def generate_recommendation(
    request: RecommendationRequest,
    recommendation_service: AITransportationRecommendationService = Depends(get_recommendation_service)
) -> RecommendationResponse:
    """
    Generate AI-powered transportation recommendations.
    
    Args:
        request: Recommendation request containing aggregated transportation data
        recommendation_service: AI recommendation service instance
        
    Returns:
        RecommendationResponse: Structured recommendation with analysis and alternatives
        
    Raises:
        HTTPException: For validation errors or service failures
    """
    try:
        logger.info(f"Generating recommendation for lane: {request.source_city} to {request.destination_city}")
        
        # Validate that we have sufficient data for analysis
        if not request.aggregated_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aggregated data is required for recommendation generation"
            )
        
        # Check if we have at least one valid data source
        valid_sources = sum(1 for value in request.aggregated_data.values() if value)
        if valid_sources == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one valid data source is required in aggregated_data"
            )
        
        # Generate the recommendation using the enhanced AI service
        recommendation = await recommendation_service.generate_recommendation(request)
        
        logger.info(
            f"Successfully generated recommendation with confidence: {recommendation.confidence_score:.2%}"
        )
        
        return recommendation
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except RAGChatbotException as e:
        logger.error(f"RAG Chatbot error during recommendation generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation service error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during recommendation generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate transportation recommendation"
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Check Recommendation Service Health",
    description="Check if the AI Transportation Recommendation Service is healthy and ready."
)
async def check_recommendation_health(
    recommendation_service: AITransportationRecommendationService = Depends(get_recommendation_service)
) -> Dict[str, Any]:
    """
    Health check endpoint for the recommendation service.
    
    Args:
        recommendation_service: AI recommendation service instance
        
    Returns:
        Dict containing health status and service information
    """
    try:
        # Verify that the service can be initialized and has required configuration
        has_openai_key = bool(recommendation_service.llm.openai_api_key)
        
        return {
            "status": "healthy",
            "service": "AI Transportation Recommendation Service",
            "model": recommendation_service.model_name,
            "temperature": recommendation_service.temperature,
            "openai_configured": has_openai_key,
            "ready": has_openai_key
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "AI Transportation Recommendation Service",
            "error": str(e),
            "ready": False
        }


@router.post(
    "/validate-data",
    status_code=status.HTTP_200_OK,
    summary="Validate Aggregated Data Quality",
    description="""
    Validate the completeness and quality of aggregated transportation data
    before generating recommendations.
    
    This endpoint helps determine if sufficient data is available for
    meaningful recommendation generation.
    """
)
async def validate_aggregated_data(
    aggregated_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate aggregated data quality and completeness.
    
    Args:
        aggregated_data: Aggregated transportation data to validate
        
    Returns:
        Dict containing validation results and data quality metrics
    """
    try:
        # Initialize validation results
        validation_results = {
            "is_valid": False,
            "data_completeness": 0.0,
            "available_sources": [],
            "missing_sources": [],
            "recommendations": [],
            "ready_for_ai_analysis": False
        }
        
        # Expected data sources
        expected_sources = [
            ("riq_data", "RIQ Rate Analysis"),
            ("spot_data", "Spot Rate Matrix"),
            ("historical_data", "Historical Lane Data"),
            ("chat_insights", "Chat-Parsed Insights"),
            ("order_data", "Order Release Data")
        ]
        
        # Check each data source
        available_count = 0
        for source_key, source_name in expected_sources:
            if source_key in aggregated_data and aggregated_data[source_key]:
                validation_results["available_sources"].append(source_name)
                available_count += 1
            else:
                validation_results["missing_sources"].append(source_name)
        
        # Calculate data completeness
        validation_results["data_completeness"] = available_count / len(expected_sources)
        
        # Determine if data is sufficient for analysis
        if available_count >= 2:  # Need at least 2 sources for meaningful analysis
            validation_results["is_valid"] = True
            validation_results["ready_for_ai_analysis"] = True
        elif available_count == 1:
            validation_results["is_valid"] = True
            validation_results["ready_for_ai_analysis"] = False
            validation_results["recommendations"].append(
                "Limited data available. Consider gathering more sources for better recommendations."
            )
        else:
            validation_results["recommendations"].append(
                "Insufficient data for recommendation generation. Please provide transportation data."
            )
        
        # Add specific recommendations based on missing sources
        if "RIQ Rate Analysis" in validation_results["missing_sources"]:
            validation_results["recommendations"].append(
                "Consider querying RIQ rates for contract pricing analysis."
            )
        
        if "Spot Rate Matrix" in validation_results["missing_sources"]:
            validation_results["recommendations"].append(
                "Consider querying spot rates for current market pricing."
            )
        
        if "Historical Lane Data" in validation_results["missing_sources"]:
            validation_results["recommendations"].append(
                "Consider adding historical data for trend analysis."
            )
        
        logger.info(
            f"Data validation completed: {available_count}/{len(expected_sources)} sources available"
        )
        
        return validation_results
        
    except Exception as e:
        logger.error(f"Data validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate aggregated data"
        ) 