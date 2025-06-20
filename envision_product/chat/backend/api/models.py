from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Request Models
class CreateKBRequest(BaseModel):
    """Request model for creating a new knowledge base."""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the knowledge base.")
    description: Optional[str] = Field(None, max_length=500, description="Optional description for the KB.")

class ProcessKBRequest(BaseModel):
    """Request model for processing documents in a knowledge base."""
    retriever_type: str = Field("hybrid", description="Retriever type to use (e.g., standard, hybrid, multi_query, advanced_hybrid).")
    # Add other processing options if needed, e.g., chunk_size, chunk_overlap, force_reprocess

class ChatRequest(BaseModel):
    """Request model for sending a query to the chatbot."""
    query: str = Field(..., min_length=1, description="The user's query.")
    # Add other chat options if needed, e.g., session_id, temperature

class RecommendationRequest(BaseModel):
    """Request model for generating AI transportation recommendations."""
    aggregated_data: Dict[str, Any] = Field(..., description="Aggregated transportation data from various sources.")
    source_city: Optional[str] = Field(None, description="Source city for the lane.")
    destination_city: Optional[str] = Field(None, description="Destination city for the lane.")
    weight: Optional[str] = Field(None, description="Shipment weight with unit.")
    volume: Optional[str] = Field(None, description="Shipment volume with unit.")
    context: Optional[str] = Field(None, description="Additional context or requirements.")

# Response Models
class KBInfo(BaseModel):
    """Response model for knowledge base information."""
    id: str = Field(..., description="Unique identifier for the knowledge base (usually the name).")
    name: str = Field(..., description="Name of the knowledge base.")
    description: Optional[str] = Field(None, description="Description of the knowledge base.")
    document_count: int = Field(0, description="Number of documents in the KB.")
    chunk_count: int = Field(0, description="Total number of chunks in the KB.")
    status: str = Field("unknown", description="Current status of the KB (e.g., new, processing, ready, error).")
    created_at: Optional[datetime] = Field(None, description="Timestamp of KB creation.")
    last_processed_at: Optional[datetime] = Field(None, description="Timestamp of last processing.")

class DocumentInfo(BaseModel):
    """Response model for uploaded document information."""
    id: str = Field(..., description="Unique identifier for the document (e.g., filename or a generated ID).")
    filename: str = Field(..., description="Original filename of the uploaded document.")
    content_type: Optional[str] = Field(None, description="MIME type of the document.")
    size: int = Field(..., description="Size of the document in bytes.")
    kb_id: str = Field(..., description="ID of the knowledge base this document belongs to.")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of when the document was uploaded.")
    message: str = Field("File uploaded successfully", description="Status message for the upload.")

class ChatResponse(BaseModel):
    """Response model for a chatbot query."""
    answer: str = Field(..., description="The chatbot's answer to the query.")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score of the answer.")
    sources: List[Dict[str, Any]] = Field([], description="List of source documents/chunks used for the answer.")
    processing_time: Optional[float] = Field(None, description="Time taken to process the query in seconds.")
    kb_id: Optional[str] = Field(None, description="ID of the knowledge base used for this response.")
    query: Optional[str] = Field(None, description="The original query that led to this response.")
    debug_info: Optional[Dict[str, Any]] = Field(None, description="Optional debug information.")

class HealthCheckResponse(BaseModel):
    """Response model for the health check endpoint."""
    status: str = "ok"
    name: Optional[str] = None
    version: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# General Error Response Model
class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str = Field(..., description="The type of error that occurred.")
    message: str = Field(..., description="A human-readable message describing the error.")
    details: Optional[Any] = Field(None, description="Optional details about the error, can be a dict or list.")

# Historical Data Models
class HistoricalDataRequest(BaseModel):
    """Request model for querying historical transportation data."""
    source_city: Optional[str] = Field(None, description="Source city for the lane.")
    source_state: Optional[str] = Field(None, description="Source state for the lane.")
    source_country: Optional[str] = Field("US", description="Source country for the lane.")
    dest_city: Optional[str] = Field(None, description="Destination city for the lane.")
    dest_state: Optional[str] = Field(None, description="Destination state for the lane.")
    dest_country: Optional[str] = Field("US", description="Destination country for the lane.")
    transport_mode: Optional[str] = Field(None, description="Transport mode (e.g., LTL, TL).")
    limit: int = Field(50, description="Maximum number of records to return.", ge=1, le=1000)

class HistoricalRecord(BaseModel):
    """Represents a single historical transportation record."""
    source_city: str
    source_state: str
    source_country: str
    dest_city: str
    dest_state: str
    dest_country: str
    transport_mode: str = Field(..., alias="TMODE")
    cost_per_lb: Optional[float] = Field(None, alias="COST_PER_LB")
    cost_per_mile: Optional[float] = Field(None, alias="COST_PER_MILE")
    cost_per_cuft: Optional[float] = Field(None, alias="COST_PER_CUFT")
    shipment_count: Optional[int] = Field(None, alias="SHP_COUNT")
    mode_preference: Optional[str] = Field(None, alias="MODE_PREFERENCE")

    class Config:
        populate_by_name = True # Allows using alias for field names

class HistoricalDataResponse(BaseModel):
    """Response model for historical data queries."""
    records: List[HistoricalRecord] = Field(..., description="List of matching historical records.")
    total_count: int = Field(..., description="Total number of matching records found (before limit).")
    lane_summary: Dict[str, Any] = Field(..., description="Summary statistics for the queried lane.")
    cost_statistics: Dict[str, Optional[float]] = Field(..., description="Overall cost statistics for the queried lane.")
    query_parameters: HistoricalDataRequest = Field(..., description="The parameters used for this query.")

# Spot Rate Models
class SpotRateRequest(BaseModel):
    """Request model for querying spot rate matrix data."""
    source_city: Optional[str] = Field(None, description="Source city for the lane.")
    source_state: Optional[str] = Field(None, description="Source state for the lane.")
    source_country: Optional[str] = Field("US", description="Source country for the lane.")
    dest_city: Optional[str] = Field(None, description="Destination city for the lane.")
    dest_state: Optional[str] = Field(None, description="Destination state for the lane.")
    dest_country: Optional[str] = Field("US", description="Destination country for the lane.")
    shipment_date: str = Field(..., description="Base shipment date in YYYY-MM-DD format for 7-day projection.")

class CostDetail(BaseModel):
    """Represents cost details for a specific shipment date."""
    ship_date: str = Field(..., description="Shipment date in MM/DD/YYYY format.")
    total_spot_cost: str = Field(..., description="Total spot cost as string.")
    cost_currency: str = Field("USD", description="Currency code.")
    line_haul: str = Field(..., description="Line haul cost as string.")
    fuel: str = Field("0", description="Fuel cost as string.")
    quote_id: str = Field("AUTO_GENERATED", description="Quote identifier.")
    transport_mode: str = Field(..., description="Transport mode (e.g., TL, LTL).")

class CarrierSpotCost(BaseModel):
    """Represents spot costs for a single carrier across multiple dates."""
    carrier: str = Field(..., description="Carrier code/name.")
    cost_details: List[CostDetail] = Field(..., description="List of cost details for each shipment date.")

class SpotRateMatrixResponse(BaseModel):
    """Response model for spot rate matrix queries."""
    origin_city: str = Field(..., description="Origin city name.")
    origin_state: str = Field(..., description="Origin state code.")
    destination_city: str = Field(..., description="Destination city name.")
    destination_state: str = Field(..., description="Destination state code.")
    shipment_date: str = Field(..., description="Base shipment date in MM/DD/YYYY format.")
    spot_costs: List[CarrierSpotCost] = Field(..., description="List of carriers with their cost details.")
    query_parameters: SpotRateRequest = Field(..., description="The parameters used for this query.")

class RecommendationAlternative(BaseModel):
    """Represents an alternative transportation option."""
    option_name: str = Field(..., description="Name of the alternative option.")
    carrier: Optional[str] = Field(None, description="Recommended carrier for this option.")
    estimated_cost: Optional[str] = Field(None, description="Estimated cost for this option.")
    transit_time: Optional[str] = Field(None, description="Expected transit time.")
    risk_level: str = Field(..., description="Risk assessment (Low, Medium, High).")
    reasoning: str = Field(..., description="Reasoning for this alternative.")

class CostOptimizationAnalysis(BaseModel):
    """Represents cost optimization analysis between RIQ and spot rates."""
    strategy_type: str = Field(..., description="Type of strategy (RIQ_CONTRACT, SPOT_MARKET, HYBRID).")
    estimated_savings: Optional[str] = Field(None, description="Estimated cost savings.")
    risk_assessment: str = Field(..., description="Risk level of this strategy.")
    market_timing: str = Field(..., description="Market timing recommendations.")
    reasoning: str = Field(..., description="Detailed reasoning for this strategy.")

class RiskAssessment(BaseModel):
    """Represents transportation risk assessment."""
    overall_risk_level: str = Field(..., description="Overall risk level (Low, Medium, High).")
    performance_risk: Optional[str] = Field(None, description="Performance risk based on historical data.")
    market_risk: Optional[str] = Field(None, description="Market volatility risk.")
    capacity_risk: Optional[str] = Field(None, description="Capacity availability risk.")
    mitigation_strategies: List[str] = Field(default_factory=list, description="Risk mitigation recommendations.")

class RecommendationMetadata(BaseModel):
    """Metadata about the recommendation generation process."""
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence in the recommendation.")
    data_sources_used: List[str] = Field(..., description="List of data sources used for the recommendation.")
    data_completeness: float = Field(..., ge=0.0, le=1.0, description="Completeness of available data.")
    processing_notes: List[str] = Field(default_factory=list, description="Notes about the processing.")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of generation.")

class RecommendationResponse(BaseModel):
    """Response model for AI transportation recommendations."""
    primary_recommendation: str = Field(..., description="Primary transportation recommendation with detailed reasoning.")
    recommended_carrier: Optional[str] = Field(None, description="Primary recommended carrier.")
    estimated_cost: Optional[str] = Field(None, description="Estimated cost for primary recommendation.")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the recommendation.")
    
    cost_optimization: CostOptimizationAnalysis = Field(..., description="Cost optimization analysis.")
    risk_assessment: RiskAssessment = Field(..., description="Risk assessment and mitigation strategies.")
    alternatives: List[RecommendationAlternative] = Field(default_factory=list, description="Alternative transportation options.")
    market_timing: str = Field(..., description="Market timing and timing recommendations.")
    
    metadata: RecommendationMetadata = Field(..., description="Metadata about the recommendation process.")
    raw_ai_response: str = Field(..., description="Raw response from the AI model.")
    structured_data: Dict[str, Any] = Field(default_factory=dict, description="Structured data extracted from the response.")
    
    # Lane information
    source_city: Optional[str] = Field(None, description="Source city.")
    destination_city: Optional[str] = Field(None, description="Destination city.")
    lane_name: Optional[str] = Field(None, description="Full lane description.") 