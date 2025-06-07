"""
AI Transportation Recommendation Service

This service leverages the same model configuration and sophisticated prompting techniques
from enhanced_rc.py to generate intelligent transportation recommendations based on 
aggregated market data.
"""

import os
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

from ..models import (
    RecommendationRequest, 
    RecommendationResponse,
    RecommendationAlternative,
    CostOptimizationAnalysis,
    RiskAssessment,
    RecommendationMetadata
)

logger = logging.getLogger(__name__)


class AITransportationRecommendationService:
    """
    AI-powered transportation recommendation service using the same model configuration
    and prompting techniques as the enhanced RAG chain.
    """
    
    def __init__(self, temperature: float = 1, model_name: str = "o4-mini-2025-04-16"):
        """
        Initialize the recommendation service with the same configuration as enhanced_rc.py.
        
        Args:
            temperature: Model temperature (default 0.7 matching enhanced_rc.py)
            model_name: Model name (default "gpt-4o-mini" matching enhanced_rc.py)
        """
        self.temperature = temperature
        self.model_name = model_name
        
        # Use the same ChatOpenAI configuration from enhanced_rc.py
        self.llm = ChatOpenAI(
            temperature=temperature,
            model_name=model_name,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Create the sophisticated prompt template adapted for recommendations
        self.prompt_template = self._create_recommendation_prompt_template()
        
    def _create_recommendation_prompt_template(self) -> PromptTemplate:
        """
        Create a sophisticated recommendation prompt template based on enhanced_rc.py patterns.
        This adapts the same structured approach for transportation recommendations.
        """
        template = """You are an expert transportation and logistics consultant analyzing carrier data to provide optimal shipping recommendations.

**ANALYSIS FRAMEWORK:**

1. **Performance Classification:**
   - Tier 1 (Premium): >90% on-time performance
   - Tier 2 (Standard): 80-90% on-time performance  
   - Tier 3 (Risk): <80% on-time performance

2. **Recommendation Logic:**
   - If the cheapest SPOT rate is 10% less than the cheapest RIQ Rate or best performing carrier RIQ Rate, then recommend the cheapest SPOT rate.
        - Choose the cheapest option from the SPOT rate matrix for the carrier and the date, not the AVERAGE cost.
   - Select lowest cost option from Tier 1 or Tier 2 carriers only
   - If no Tier 1/2 options exist, choose lowest cost overall but flag as high risk
   - If cheapest option is >20% more expensive than alternatives, recommend hybrid approach

3. **Cost Analysis:**
   - Compare all RIQ contract rates
   - Compare all spot market rates
   - Calculate percentage savings between options

**REQUIRED RESPONSE FORMAT:**

🎯 **Transportation Recommendation** (Confidence: XX%)

**PRIMARY RECOMMENDATION:** [Carrier Name] via [RIQ Contract/Spot Market] at $[amount]

**REASONING:**
- Cost: $[amount] ([X]% vs next best alternative)
- Performance: [On-time %] (Tier [1/2/3])
- Risk Level: [Low/Medium/High]

**ALTERNATIVES:**
- Option 2: [Carrier] at $[amount] ([RIQ/Spot])
- Option 3: [Carrier] at $[amount] ([RIQ/Spot])

**MARKET TIMING:** [Immediate/Monitor/Delayed] - [brief reasoning]

---STRUCTURED_OUTPUT---
PRIMARY_CARRIER: [Name]
STRATEGY: [RIQ_CONTRACT/SPOT_MARKET]
COST: $[amount] Date: [date]
CONFIDENCE: [XX%]
TIMING: [IMMEDIATE/DELAYED/MONITOR]
PERFORMANCE_TIER: [1/2/3]
LANE: [source] to [destination]
---END---

**INPUT DATA:**
Carriers: {aggregated_data}
Lane: {source_city} to {destination_city}
Shipment Details: {weight} lbs, {volume} cubic feet
Context: {context}"""
        
        return PromptTemplate(
            template=template,
            input_variables=[
                "aggregated_data", "source_city", "destination_city", 
                "weight", "volume", "context"
            ]
        )
    
    async def generate_recommendation(self, request: RecommendationRequest) -> RecommendationResponse:
        """
        Generate AI transportation recommendations using the enhanced prompting approach.
        
        Args:
            request: Recommendation request with aggregated data
            
        Returns:
            Structured recommendation response
        """
        try:
            # Prepare the aggregated data for analysis
            formatted_data = self._format_aggregated_data(request.aggregated_data)
            
            # Generate the prompt using the template
            prompt = self.prompt_template.format(
                aggregated_data=formatted_data,
                source_city=request.source_city or "Not specified",
                destination_city=request.destination_city or "Not specified",
                weight=request.weight or "Not specified",
                volume=request.volume or "Not specified",
                context=request.context or "No additional context"
            )
            
            # Call the LLM with the same approach as enhanced_rc.py
            message = HumanMessage(content=prompt)
            response = await self.llm.agenerate([[message]])
            raw_response = response.generations[0][0].text
            
            # Post-process the response using enhanced techniques
            processed_response = self._post_process_response(
                raw_response, request.aggregated_data
            )
            
            return processed_response
            
        except Exception as e:
            logger.error(f"Failed to generate recommendation: {str(e)}")
            return self._create_error_response(str(e), request)
    
    def _format_aggregated_data(self, aggregated_data: Dict[str, Any]) -> str:
        """
        Format aggregated data for AI analysis, similar to enhanced_rc.py data formatting.
        
        Args:
            aggregated_data: Raw aggregated data from various sources
            
        Returns:
            Formatted data string for prompt inclusion
        """
        formatted_sections = []
        
        # RIQ Rate Data
        if "riq_data" in aggregated_data:
            riq_data = aggregated_data["riq_data"]
            formatted_sections.append("**RIQ RATE ANALYSIS:**")
            if isinstance(riq_data, dict):
                for key, value in riq_data.items():
                    if isinstance(value, (dict, list)):
                        formatted_sections.append(f"- {key}: {json.dumps(value, indent=2)}")
                    else:
                        formatted_sections.append(f"- {key}: {value}")
            else:
                formatted_sections.append(f"- Data: {riq_data}")
        
        # Spot Rate Matrix Data
        if "spot_data" in aggregated_data:
            spot_data = aggregated_data["spot_data"]
            formatted_sections.append("\n**SPOT RATE MATRIX:**")
            if isinstance(spot_data, dict):
                if "spot_costs" in spot_data:
                    formatted_sections.append(f"- Carriers Available: {len(spot_data['spot_costs'])}")
                    for carrier_data in spot_data["spot_costs"][:5]:  # Limit to first 5 carriers
                        carrier_name = carrier_data.get("carrier", "Unknown")
                        cost_details = carrier_data.get("cost_details", [])
                        if cost_details:
                            avg_cost = sum(float(detail.get("total_spot_cost", 0)) for detail in cost_details) / len(cost_details)
                            formatted_sections.append(f"  - {carrier_name}: Average ${avg_cost:.2f}")
                else:
                    formatted_sections.append(f"- Spot Data: {json.dumps(spot_data, indent=2)[:500]}...")
        
        # Historical Data
        if "historical_data" in aggregated_data:
            hist_data = aggregated_data["historical_data"]
            formatted_sections.append("\n**HISTORICAL LANE PERFORMANCE:**")
            if isinstance(hist_data, dict):
                if "cost_statistics" in hist_data:
                    stats = hist_data["cost_statistics"]
                    formatted_sections.append(f"- Average Cost per Mile: ${stats.get('avg_cost_per_mile', 'N/A')}")
                    formatted_sections.append(f"- Average Cost per Lb: ${stats.get('avg_cost_per_lb', 'N/A')}")
                if "lane_summary" in hist_data:
                    summary = hist_data["lane_summary"]
                    formatted_sections.append(f"- Most Common Mode: {summary.get('most_common_mode', 'N/A')}")
                    formatted_sections.append(f"- Historical Records: {hist_data.get('total_count', 'N/A')}")
        
        # Chat Analysis (Best/Worst Performers)
        if "chat_insights" in aggregated_data:
            chat_data = aggregated_data["chat_insights"]
            formatted_sections.append("\n**CHAT-PARSED INSIGHTS:**")
            if isinstance(chat_data, dict):
                if "best_performer" in chat_data:
                    best = chat_data["best_performer"]
                    formatted_sections.append(f"- Best Performer: {best.get('carrier', 'Unknown')} ({best.get('performance', 'N/A')})")
                if "worst_performer" in chat_data:
                    worst = chat_data["worst_performer"]
                    formatted_sections.append(f"- Worst Performer: {worst.get('carrier', 'Unknown')} ({worst.get('performance', 'N/A')})")
        
        # Order Release Data
        if "order_data" in aggregated_data:
            order_data = aggregated_data["order_data"]
            formatted_sections.append("\n**UNPLANNED ORDER ANALYSIS:**")
            if isinstance(order_data, list):
                formatted_sections.append(f"- Unplanned Orders: {len(order_data)}")
                if order_data:
                    # Sample first few orders
                    for i, order in enumerate(order_data[:3]):
                        formatted_sections.append(f"  - Order {i+1}: {order}")
        
        # Additional data sources
        for key, value in aggregated_data.items():
            if key not in ["riq_data", "spot_data", "historical_data", "chat_insights", "order_data"]:
                formatted_sections.append(f"\n**{key.upper()}:**")
                if isinstance(value, (dict, list)):
                    formatted_sections.append(json.dumps(value, indent=2)[:300] + "...")
                else:
                    formatted_sections.append(str(value))
        
        return "\n".join(formatted_sections)
    
    def _post_process_response(
        self, 
        raw_response: str, 
        aggregated_data: Dict[str, Any]
    ) -> RecommendationResponse:
        """
        Post-process the AI response using enhanced techniques from enhanced_rc.py.
        
        Args:
            raw_response: Raw AI model response
            aggregated_data: Original aggregated data
            
        Returns:
            Structured recommendation response
        """
        # Extract structured data using regex patterns similar to enhanced_rc.py
        structured_data = self._extract_structured_data(raw_response)
        
        # Parse main components from the response
        primary_recommendation = self._extract_primary_recommendation(raw_response)
        cost_optimization = self._extract_cost_optimization(raw_response)
        risk_assessment = self._extract_risk_assessment(raw_response)
        alternatives = self._extract_alternatives(raw_response)
        market_timing = self._extract_market_timing(raw_response)
        
        # Calculate confidence score using enhanced methodology
        confidence_score = self._calculate_confidence_score(raw_response, aggregated_data)
        
        # Generate metadata using enhanced patterns
        metadata = self._generate_metadata(raw_response, aggregated_data, confidence_score)
        
        return RecommendationResponse(
            primary_recommendation=primary_recommendation,
            recommended_carrier=structured_data.get("PRIMARY_CARRIER"),
            estimated_cost=structured_data.get("ESTIMATED_COST"),
            confidence_score=confidence_score,
            cost_optimization=cost_optimization,
            risk_assessment=risk_assessment,
            alternatives=alternatives,
            market_timing=market_timing,
            metadata=metadata,
            raw_ai_response=raw_response,
            structured_data=structured_data,
            source_city=structured_data.get("LANE", "").split(" to ")[0] if " to " in structured_data.get("LANE", "") else None,
            destination_city=structured_data.get("LANE", "").split(" to ")[1] if " to " in structured_data.get("LANE", "") else None,
            lane_name=structured_data.get("LANE")
        )
    
    def _extract_structured_data(self, response: str) -> Dict[str, Any]:
        """
        Extract structured data from response using regex patterns like enhanced_rc.py.
        
        Args:
            response: AI model response
            
        Returns:
            Dictionary of extracted structured data
        """
        structured_data = {}
        
        # Look for the structured data section
        pattern = r"---STRUCTURED_RECOMMENDATION---(.*?)---END_STRUCTURED_RECOMMENDATION---"
        match = re.search(pattern, response, re.DOTALL)
        
        if match:
            structured_section = match.group(1)
            
            # Extract each field
            fields = [
                "PRIMARY_CARRIER", "PRIMARY_STRATEGY", "ESTIMATED_COST",
                "CONFIDENCE_LEVEL", "RISK_LEVEL", "MARKET_TIMING",
                "DATA_COMPLETENESS", "ALTERNATIVE_COUNT", "LANE"
            ]
            
            for field in fields:
                field_pattern = f"{field}:\\s*(.+?)(?=\\n|$)"
                field_match = re.search(field_pattern, structured_section)
                if field_match:
                    value = field_match.group(1).strip()
                    if value and value != "N/A":
                        structured_data[field] = value
        
        return structured_data
    
    def _extract_primary_recommendation(self, response: str) -> str:
        """Extract the primary recommendation section from the response."""
        # Look for content between PRIMARY RECOMMENDATION and COST OPTIMIZATION
        pattern = r"PRIMARY RECOMMENDATION:\s*(.*?)(?=COST OPTIMIZATION|RISK ASSESSMENT|ALTERNATIVE OPTIONS|$)"
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        # Fallback: look for the main recommendation content
        lines = response.split('\n')
        recommendation_lines = []
        in_recommendation = False
        
        for line in lines:
            if 'recommendation' in line.lower() and ('🎯' in line or '**' in line):
                in_recommendation = True
                recommendation_lines.append(line)
            elif in_recommendation:
                if any(keyword in line.upper() for keyword in ['COST OPTIMIZATION', 'RISK ASSESSMENT', 'ALTERNATIVE']):
                    break
                recommendation_lines.append(line)
        
        return '\n'.join(recommendation_lines).strip() if recommendation_lines else "Primary recommendation not clearly identified."
    
    def _extract_cost_optimization(self, response: str) -> CostOptimizationAnalysis:
        """Extract cost optimization analysis from the response."""
        # Look for cost optimization section
        pattern = r"COST OPTIMIZATION.*?:\s*(.*?)(?=RISK ASSESSMENT|ALTERNATIVE OPTIONS|MARKET TIMING|$)"
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        
        content = match.group(1).strip() if match else "Cost optimization analysis not found."
        
        # Determine strategy type from content
        strategy_type = "HYBRID"
        if any(term in content.upper() for term in ["RIQ", "CONTRACT"]):
            strategy_type = "RIQ_CONTRACT"
        elif any(term in content.upper() for term in ["SPOT", "MARKET"]):
            strategy_type = "SPOT_MARKET"
        
        # Extract savings estimate
        savings_match = re.search(r"\$[\d,]+(?:\.\d{2})?|\d+%", content)
        estimated_savings = savings_match.group(0) if savings_match else None
        
        return CostOptimizationAnalysis(
            strategy_type=strategy_type,
            estimated_savings=estimated_savings,
            risk_assessment="Medium",  # Default
            market_timing="Evaluate current conditions",
            reasoning=content
        )
    
    def _extract_risk_assessment(self, response: str) -> RiskAssessment:
        """Extract risk assessment from the response."""
        pattern = r"RISK ASSESSMENT.*?:\s*(.*?)(?=ALTERNATIVE OPTIONS|MARKET TIMING|STRUCTURED|$)"
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        
        content = match.group(1).strip() if match else "Risk assessment not found."
        
        # Determine overall risk level
        risk_level = "MEDIUM"
        if any(term in content.upper() for term in ["LOW RISK", "MINIMAL RISK"]):
            risk_level = "LOW"
        elif any(term in content.upper() for term in ["HIGH RISK", "SIGNIFICANT RISK"]):
            risk_level = "HIGH"
        
        # Extract mitigation strategies
        mitigation_strategies = []
        if "mitigation" in content.lower():
            # Look for bullet points or numbered lists
            strategies = re.findall(r"[-•*]\s*(.+?)(?=\n|$)", content)
            mitigation_strategies = [s.strip() for s in strategies if s.strip()]
        
        return RiskAssessment(
            overall_risk_level=risk_level,
            performance_risk="Based on historical data",
            market_risk="Market volatility considerations",
            capacity_risk="Capacity availability factors",
            mitigation_strategies=mitigation_strategies or ["Monitor market conditions", "Maintain backup options"]
        )
    
    def _extract_alternatives(self, response: str) -> List[RecommendationAlternative]:
        """Extract alternative options from the response."""
        pattern = r"ALTERNATIVE OPTIONS.*?:\s*(.*?)(?=MARKET TIMING|CONFIDENCE|STRUCTURED|$)"
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        
        content = match.group(1).strip() if match else ""
        alternatives = []
        
        if content:
            # Look for numbered or bulleted alternatives
            alt_patterns = [
                r"(\d+)\.\s*(.+?)(?=\d+\.|$)",
                r"[-•*]\s*(.+?)(?=[-•*]|$)"
            ]
            
            for pattern in alt_patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                for match in matches:
                    alt_text = match[1] if len(match) > 1 else match[0]
                    alt_text = alt_text.strip()
                    
                    if len(alt_text) > 10:  # Ensure meaningful content
                        alternatives.append(RecommendationAlternative(
                            option_name=f"Alternative {len(alternatives) + 1}",
                            carrier=None,  # Could be extracted with more parsing
                            estimated_cost=None,
                            transit_time=None,
                            risk_level="Medium",
                            reasoning=alt_text
                        ))
                
                if alternatives:
                    break
        
        # Ensure at least one alternative
        if not alternatives:
            alternatives.append(RecommendationAlternative(
                option_name="Backup Strategy",
                carrier=None,
                estimated_cost=None,
                transit_time=None,
                risk_level="Medium",
                reasoning="Alternative transportation options should be evaluated based on market conditions."
            ))
        
        return alternatives[:3]  # Limit to 3 alternatives
    
    def _extract_market_timing(self, response: str) -> str:
        """Extract market timing recommendations from the response."""
        pattern = r"MARKET TIMING.*?:\s*(.*?)(?=CONFIDENCE|STRUCTURED|$)"
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        return "Evaluate current market conditions and timing for optimal procurement."
    
    def _calculate_confidence_score(
        self, 
        response: str, 
        aggregated_data: Dict[str, Any]
    ) -> float:
        """
        Calculate confidence score using enhanced methodology from enhanced_rc.py.
        
        Args:
            response: AI model response
            aggregated_data: Original aggregated data
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence from data completeness
        data_sources = len([k for k, v in aggregated_data.items() if v])
        data_completeness_factor = min(data_sources / 4.0, 1.0)  # Expect up to 4 main sources
        
        # Check for uncertainty phrases (similar to enhanced_rc.py)
        uncertainty_phrases = [
            "insufficient data", "limited information", "uncertain",
            "unclear", "might be", "possibly", "appears to",
            "seems", "may be", "could be"
        ]
        
        uncertainty_penalty = 0.0
        response_lower = response.lower()
        for phrase in uncertainty_phrases:
            if phrase in response_lower:
                uncertainty_penalty += 0.15
                if uncertainty_penalty >= 0.3:  # Cap penalty
                    break
        
        # Response completeness factor
        completeness_factor = 0.0
        required_sections = [
            "primary recommendation", "cost optimization", "risk assessment",
            "alternative", "market timing"
        ]
        
        for section in required_sections:
            if section in response_lower:
                completeness_factor += 0.1
        
        # Structured data bonus
        structured_bonus = 0.1 if "---STRUCTURED_RECOMMENDATION---" in response else 0.0
        
        # Calculate final confidence
        confidence = (
            0.3 +  # Base confidence
            data_completeness_factor * 0.3 +  # Data quality factor
            completeness_factor +  # Response completeness
            structured_bonus  # Structured output bonus
        ) - uncertainty_penalty
        
        return max(0.1, min(1.0, confidence))
    
    def _generate_metadata(
        self, 
        response: str, 
        aggregated_data: Dict[str, Any], 
        confidence_score: float
    ) -> RecommendationMetadata:
        """
        Generate metadata using enhanced patterns from enhanced_rc.py.
        
        Args:
            response: AI model response
            aggregated_data: Original aggregated data
            confidence_score: Calculated confidence score
            
        Returns:
            Recommendation metadata
        """
        # Identify data sources used
        data_sources_used = []
        if "riq_data" in aggregated_data and aggregated_data["riq_data"]:
            data_sources_used.append("RIQ Rate Analysis")
        if "spot_data" in aggregated_data and aggregated_data["spot_data"]:
            data_sources_used.append("Spot Rate Matrix")
        if "historical_data" in aggregated_data and aggregated_data["historical_data"]:
            data_sources_used.append("Historical Lane Data")
        if "chat_insights" in aggregated_data and aggregated_data["chat_insights"]:
            data_sources_used.append("Chat-Parsed Insights")
        if "order_data" in aggregated_data and aggregated_data["order_data"]:
            data_sources_used.append("Order Release Data")
        
        # Calculate data completeness
        total_possible_sources = 5  # Expected number of data sources
        data_completeness = len(data_sources_used) / total_possible_sources
        
        # Generate processing notes
        processing_notes = []
        
        if data_completeness < 0.5:
            processing_notes.append("Limited data sources available - consider gathering more market data")
        
        if confidence_score < 0.6:
            processing_notes.append("Recommendation based on limited information - validate with additional sources")
        
        if len(data_sources_used) >= 3:
            processing_notes.append("Recommendation synthesized from multiple data sources")
        
        if "insufficient" in response.lower() or "limited" in response.lower():
            processing_notes.append("AI indicated data limitations in analysis")
        
        return RecommendationMetadata(
            confidence_score=confidence_score,
            data_sources_used=data_sources_used,
            data_completeness=data_completeness,
            processing_notes=processing_notes,
            generated_at=datetime.utcnow()
        )
    
    def _create_error_response(
        self, 
        error_message: str, 
        request: RecommendationRequest
    ) -> RecommendationResponse:
        """
        Create an error response when recommendation generation fails.
        
        Args:
            error_message: Error description
            request: Original request
            
        Returns:
            Error recommendation response
        """
        return RecommendationResponse(
            primary_recommendation=f"Unable to generate recommendation due to error: {error_message}",
            recommended_carrier=None,
            estimated_cost=None,
            confidence_score=0.1,
            cost_optimization=CostOptimizationAnalysis(
                strategy_type="HYBRID",
                estimated_savings=None,
                risk_assessment="High",
                market_timing="Unable to assess",
                reasoning="Error in analysis prevents cost optimization recommendations."
            ),
            risk_assessment=RiskAssessment(
                overall_risk_level="HIGH",
                performance_risk="Unable to assess",
                market_risk="Unable to assess",
                capacity_risk="Unable to assess",
                mitigation_strategies=["Retry analysis with corrected data", "Consult manual analysis"]
            ),
            alternatives=[],
            market_timing="Unable to provide timing recommendations due to analysis error.",
            metadata=RecommendationMetadata(
                confidence_score=0.1,
                data_sources_used=[],
                data_completeness=0.0,
                processing_notes=[f"Analysis failed: {error_message}"],
                generated_at=datetime.utcnow()
            ),
            raw_ai_response=f"Error: {error_message}",
            structured_data={},
            source_city=request.source_city,
            destination_city=request.destination_city,
            lane_name=f"{request.source_city} to {request.destination_city}" if request.source_city and request.destination_city else None
        ) 