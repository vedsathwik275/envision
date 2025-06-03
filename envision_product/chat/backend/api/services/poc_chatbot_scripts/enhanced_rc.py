from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import BaseRetriever, Document
from typing import List, Dict, Any, Optional
import os
from pydantic import Field

class EnhancedRAGChain:
    def __init__(self, vectorstore, temperature=0.7, model_name="gpt-4o-mini", retriever=None):
        self.vectorstore = vectorstore
        self.temperature = temperature
        self.model_name = model_name
        self.custom_retriever = retriever
        
        # Use ChatOpenAI for better responses
        if "gpt-3.5" in model_name or "gpt-4" in model_name:
            self.llm = ChatOpenAI(
                temperature=temperature, 
                model_name=model_name,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        else:
            self.llm = OpenAI(
                temperature=temperature,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        
    def create_enhanced_retriever_class(self):
        """Create the enhanced retriever class using composition"""
        
        class EnhancedRetriever(BaseRetriever):
            def __init__(self, base_retriever):
                super().__init__()
                # Store as private attribute to avoid Pydantic validation
                self._base_retriever = base_retriever
            
            def _get_relevant_documents(self, query: str) -> List[Document]:
                # Try multiple query formats for better CSV matching
                queries_to_try = [
                    query,  # Original query
                ]
                
                # Extract city names and create alternative formats
                import re
                
                # Look for "source city X and destination city Y" pattern
                source_dest_match = re.search(r'source city\s+([a-zA-Z\s]+?)\s+and\s+destination city\s+([a-zA-Z\s]+)', query, re.IGNORECASE)
                if source_dest_match:
                    source = source_dest_match.group(1).strip().upper()
                    dest = source_dest_match.group(2).strip().upper()
                    
                    # Add CSV-like formats
                    queries_to_try.extend([
                        f"{source},{dest}",
                        f"{source} {dest}",
                        f"{source} to {dest}",
                        f"from {source} to {dest}",
                        f"carrier {source} {dest}",
                        f"ODFL {source} {dest}",  # Common carrier
                        f"predicted_ontime_performance {source} {dest}"
                    ])
                
                # Look for "lane X to Y" pattern
                lane_match = re.search(r'lane\s+([a-zA-Z\s]+?)\s+to\s+([a-zA-Z\s]+)', query, re.IGNORECASE)
                if lane_match:
                    source = lane_match.group(1).strip().upper()
                    dest = lane_match.group(2).strip().upper()
                    
                    queries_to_try.extend([
                        f"{source},{dest}",
                        f"{source} {dest}",
                        f"ODFL {source} {dest}"
                    ])
                
                # Collect documents from all query variants
                all_docs = []
                seen_content = set()
                
                for q in queries_to_try:
                    try:
                        docs = self._base_retriever.get_relevant_documents(q)
                        for doc in docs:
                            # Avoid duplicates based on content
                            content_hash = hash(doc.page_content[:100])
                            if content_hash not in seen_content:
                                seen_content.add(content_hash)
                                all_docs.append(doc)
                    except Exception:
                        continue
                
                # Return top results, prioritizing variety
                return all_docs[:8]  # Increased from default
        
        return EnhancedRetriever
    
    def create_advanced_prompt(self):
        """Create a more sophisticated prompt template"""
        template = """You are an expert assistant analyzing transportation and logistics documents to provide accurate, comprehensive answers.

INSTRUCTIONS:
- Answer based ONLY on the provided context
- For transportation/logistics queries involving lanes, routes, carriers, or performance data:
  * Start your response with the exact format: "🎯 **Answer** (Confidence: [your confidence as percentage])"
  * Then immediately provide a section about the BEST performance metric found
  * Use format: "### Best Performance Analysis"
  * ALWAYS identify the carrier associated with the highest performance metric
  * Format performance details as: "The best predicted performance is [XX.XX%] for carrier [CARRIER_NAME] on the [ORIGIN], [ORIGIN_STATE], [ORIGIN_COUNTRY] to [DESTINATION], [DESTINATION_STATE], [DESTINATION_COUNTRY] lane"
  * If multiple carriers exist, clearly state which carrier achieved the highest performance
  * After the best performance, provide a section about the WORST performance metric found
  * Use format: "### Worst Performance Analysis"
  * ALWAYS identify the carrier associated with the lowest performance metric
  * Format performance details as: "The worst predicted performance is [XX.XX%] for carrier [CARRIER_NAME] on the [ORIGIN], [ORIGIN_STATE], [ORIGIN_COUNTRY] to [DESTINATION], [DESTINATION_STATE], [DESTINATION_COUNTRY] lane"
  * This helps identify carriers that might be cheapest but have poor performance
  * DO NOT repeat the confidence header - use it only once at the beginning
  * Focus on the highest/best performance value found in the data and its associated carrier, followed by the lowest/worst performance
  * CRITICAL: Always end your response with a structured data section in this exact format:
  
  ---STRUCTURED_DATA---
  LANE: [Source City, Source State, Source Country] to [Destination City, Destination State, Destination Country]
  BEST_CARRIER: [Carrier Name]
  BEST_PERFORMANCE: [XX.XX%]
  WORST_CARRIER: [Carrier Name]
  WORST_PERFORMANCE: [XX.XX%]
  ORDER_WEIGHT: [Weight with unit, e.g. "1000 lbs" or "N/A"]
  ORDER_VOLUME: [Volume with unit, e.g. "15 cuft" or "N/A"]
  ---END_STRUCTURED_DATA---
  
- Be specific and detailed when information is available
- If information is incomplete, acknowledge what you know and what's missing
- Structure your response clearly with main points
- Use examples and quotes from the context when relevant
- When discussing performance metrics, always highlight the best performance first with its carrier, then the worst performance with its carrier, then provide context about variations
- If no relevant information exists, clearly state "I cannot find information about this topic in the provided documents"

ADDITIONAL CONSTRAINTS:
- DO NOT mention lanes that were not specifically asked about unless directly relevant to the question
- DO NOT provide comparisons with other lanes unless the question specifically asks for comparisons
- Focus your answer on the exact lane or topic mentioned in the question
- If data for the requested lane is not available, say so directly rather than discussing other lanes
- Stick to facts from the provided context - do not infer or extrapolate beyond what is explicitly stated
- ALWAYS include the structured data section at the end, even if some fields are "N/A"

CONTEXT:
{context}

QUESTION: {question}

DETAILED ANALYSIS:
Let me examine the relevant information from the documents to provide you with a comprehensive answer, starting with the best available performance data and its associated carrier, followed by the worst performance data:

ANSWER:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def create_chain(self):
        """Create the standard RAG chain"""
        prompt = self.create_advanced_prompt()
        
        # Use custom retriever if provided, otherwise create from vectorstore
        if self.custom_retriever:
            retriever = self.custom_retriever
        else:
            retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": 6, "fetch_k": 20}  # Increased to get more diverse results
            )
        
        # Create the enhanced retriever class and instantiate it
        EnhancedRetriever = self.create_enhanced_retriever_class()
        enhanced_retriever = EnhancedRetriever(retriever)
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=enhanced_retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
        
        return qa_chain
    
    def create_advanced_chain(self):
        """Create advanced chain with post-processing"""
        base_chain = self.create_chain()  # This now uses the enhanced retriever
        
        # Wrap the chain to add post-processing
        class EnhancedChain:
            def __init__(self, base_chain, processor):
                self.base_chain = base_chain
                self.processor = processor
                # Store retriever reference for debugging
                self.retriever = base_chain.retriever if hasattr(base_chain, 'retriever') else None
            
            def __call__(self, inputs):
                # Get base result
                result = self.base_chain(inputs)
                
                # Post-process for enhanced output
                return self.processor.post_process_response(result)
        
        return EnhancedChain(base_chain, self)
    
    def post_process_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced response post-processing"""
        answer = result.get('result', '')
        sources = result.get('source_documents', [])
        
        # Extract performance metrics from sources for transportation data
        performance_metrics = self.extract_performance_metrics(sources)
        best_performance = self.find_best_performance(performance_metrics)
        worst_performance = self.find_worst_performance(performance_metrics)
        
        # Analyze source diversity
        source_files = set()
        source_types = set()
        
        processed_sources = []
        for doc in sources:
            source_file = doc.metadata.get('source_file', 'Unknown')
            file_type = doc.metadata.get('file_type', 'Unknown')
            
            source_files.add(source_file)
            source_types.add(file_type)
            
            processed_sources.append({
                'file': source_file,
                'type': file_type,
                'content_preview': doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                'relevance_score': getattr(doc, 'score', None),
                'metadata': doc.metadata
            })
        
        # Confidence scoring
        confidence_score = self.calculate_confidence(answer, sources)
        
        # Enhance answer format if it doesn't start with best performance and we have performance data
        enhanced_answer = self.enhance_answer_with_performance(answer, best_performance, worst_performance, confidence_score)
        
        return {
            'result': enhanced_answer,  # Keep original key for compatibility
            'answer': enhanced_answer,  # Also provide as 'answer'
            'source_documents': sources,  # Keep original
            'sources': processed_sources,  # Enhanced sources
            'source_diversity': {
                'unique_files': len(source_files),
                'file_types': list(source_types)
            },
            'confidence_score': confidence_score,
            'performance_metrics': performance_metrics,
            'best_performance': best_performance,
            'worst_performance': worst_performance,
            'metadata': {
                'total_sources_found': len(sources),
                'processing_notes': self.get_processing_notes(answer, sources)
            }
        }
    
    def extract_performance_metrics(self, sources: List) -> List[Dict[str, Any]]:
        """Extract performance metrics from source documents"""
        metrics = []
        
        # Debug: Log what sources we're getting
        print(f"DEBUG: Processing {len(sources)} source documents")
        
        for i, doc in enumerate(sources):
            content = doc.page_content.lower()
            
            # Debug: Log content snippets
            print(f"DEBUG: Source {i+1} content snippet: {content[:200]}...")
            
            # Look for REDLANDS and SHELBY specifically for debugging
            if 'redlands' in content and 'shelby' in content:
                print(f"DEBUG: Found REDLANDS-SHELBY content in source {i+1}")
            
            # Look for percentage values that might be performance metrics
            import re
            percentage_pattern = r'(\d+\.?\d*)\s*%'
            percentages = re.findall(percentage_pattern, content)
            
            # Look for specific performance indicators
            performance_indicators = [
                'predicted_ontime_performance', 'on_time_performance', 'ontime_performance',
                'delivery_performance', 'performance_score', 'reliability',
                'success_rate', 'completion_rate'
            ]
            
            for indicator in performance_indicators:
                if indicator in content:
                    # Try to extract the associated percentage
                    indicator_pattern = f'{indicator}[:\s]*(\d+\.?\d*)'
                    matches = re.findall(indicator_pattern, content)
                    for match in matches:
                        metrics.append({
                            'type': indicator,
                            'value': float(match),
                            'source_file': doc.metadata.get('source_file', 'Unknown'),
                            'carrier': self.extract_carrier_from_content(content),
                            'lane': self.extract_lane_from_content(content)
                        })
            
            # Also add standalone percentages that might be performance metrics
            for pct in percentages:
                try:
                    pct_value = float(pct)
                    if 0 <= pct_value <= 100:  # Valid percentage range
                        metrics.append({
                            'type': 'percentage_metric',
                            'value': pct_value,
                            'source_file': doc.metadata.get('source_file', 'Unknown'),
                            'carrier': self.extract_carrier_from_content(content),
                            'lane': self.extract_lane_from_content(content)
                        })
                except ValueError:
                    continue
        
        # Debug: Log extracted metrics
        print(f"DEBUG: Extracted {len(metrics)} metrics")
        for metric in metrics:
            print(f"DEBUG: Metric - {metric['type']}: {metric['value']}% for {metric['carrier']} on {metric['lane']}")
        
        return metrics
    
    def extract_carrier_from_content(self, content: str) -> Optional[str]:
        """Extract carrier name from content"""
        import re
        
        # Common carrier patterns
        carrier_patterns = [
            r'carrier[:\s]+([A-Z][A-Za-z\s&.-]+)',
            r'\b(ODFL|Old Dominion|UPS|FedEx|YRC|XPO|JB Hunt|Werner|Schneider|Swift|Knight)\b'
        ]
        
        for pattern in carrier_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def extract_lane_from_content(self, content: str) -> Optional[str]:
        """Extract lane information from content"""
        import re
        
        # Lane patterns - enhanced for CSV format
        lane_patterns = [
            # CSV format: ODFL,REDLANDS,SHELBY,82.89...
            r'([A-Z][A-Z]+),([A-Z\s]+),([A-Z\s]+),(\d+\.?\d*)',
            # Standard format: CITY to CITY
            r'([A-Z][a-zA-Z\s]+)\s+to\s+([A-Z][a-zA-Z\s]+)',
            # Metadata format: source_city: CITY dest_city: CITY  
            r'source_city[:\s]+([A-Z]+)\s+dest_city[:\s]+([A-Z]+)',
            # From X to Y format
            r'from\s+([A-Z][a-zA-Z\s]+)\s+to\s+([A-Z][a-zA-Z\s]+)',
            # Lane between format
            r'between\s+([A-Z][a-zA-Z\s]+)\s+and\s+([A-Z][a-zA-Z\s]+)',
            # Simple comma separated in text
            r'([A-Z][A-Z\s]+),\s*([A-Z][A-Z\s]+)(?:\s*,|\s*$)'
        ]
        
        for pattern in lane_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 4:  # CSV format with performance data
                    return f"{match.group(2).strip()} to {match.group(3).strip()}"
                elif len(match.groups()) >= 2:  # Standard formats
                    return f"{match.group(1).strip()} to {match.group(2).strip()}"
        
        return None
    
    def find_best_performance(self, metrics: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find the best performance metric from the list"""
        if not metrics:
            return None
        
        # Filter for actual performance metrics (not just any percentage)
        performance_metrics = [
            m for m in metrics 
            if m['type'] in ['predicted_ontime_performance', 'on_time_performance', 'ontime_performance', 
                           'delivery_performance', 'performance_score', 'reliability', "predicted_tender_performance", "predicted_tender_performance_percentage", "tender_performance", "tender_performance_percentage"]
        ]
        
        if performance_metrics:
            return max(performance_metrics, key=lambda x: x['value'])
        
        # If no specific performance metrics, use the highest percentage
        return max(metrics, key=lambda x: x['value']) if metrics else None
    
    def find_worst_performance(self, metrics: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find the worst performance metric from the list"""
        if not metrics:
            return None
        
        # Filter for actual performance metrics (not just any percentage)
        performance_metrics = [
            m for m in metrics 
            if m['type'] in ['predicted_ontime_performance', 'on_time_performance', 'ontime_performance', 
                           'delivery_performance', 'performance_score', 'reliability', "predicted_tender_performance", "predicted_tender_performance_percentage", "tender_performance", "tender_performance_percentage"]
        ]
        
        if performance_metrics:
            return min(performance_metrics, key=lambda x: x['value'])
        
        # If no specific performance metrics, use the lowest percentage
        return min(metrics, key=lambda x: x['value']) if metrics else None
    
    def enhance_answer_with_performance(self, answer: str, best_performance: Optional[Dict[str, Any]], worst_performance: Optional[Dict[str, Any]], confidence: float) -> str:
        """Enhance answer to lead with best and worst performance if not already formatted properly"""
        
        # Check if answer already starts with the target format - if so, return as-is
        if answer.startswith('🎯 **Answer**'):
            return answer
        
        # Check if answer contains the target format anywhere (not just at start)
        if '🎯 **Answer**' in answer:
            return answer
        
        # If we have performance data and the answer doesn't lead with it, enhance it
        if (best_performance or worst_performance) and not any(indicator in answer[:200].lower() for indicator in ['best', 'highest', 'maximum', 'worst', 'lowest']):
            performance_intro = f"🎯 **Answer** (Confidence: {confidence:.1%})\n"
            
            # Add best performance section
            if best_performance:
                if best_performance['carrier'] and best_performance['lane']:
                    performance_intro += f"### Best Performance: {best_performance['value']:.2f}% for {best_performance['carrier']} on {best_performance['lane']}\n\n"
                else:
                    performance_intro += f"### Best Predicted Performance: {best_performance['value']:.2f}%\n\n"
            
            # Add worst performance section
            if worst_performance:
                if worst_performance['carrier'] and worst_performance['lane']:
                    performance_intro += f"### Worst Performance: {worst_performance['value']:.2f}% for {worst_performance['carrier']} on {worst_performance['lane']}\n\n"
                else:
                    performance_intro += f"### Worst Predicted Performance: {worst_performance['value']:.2f}%\n\n"
            
            return performance_intro + answer
        
        # If no specific performance enhancement needed, just add confidence header if missing
        if not answer.startswith('🎯 **Answer**') and '🎯 **Answer**' not in answer:
            return f"🎯 **Answer** (Confidence: {confidence:.1%})\n{answer}"
        
        return answer
    
    def calculate_confidence(self, answer: str, sources: List) -> float:
        """Calculate confidence score based on various factors"""
        if not sources:
            return 0.1
        
        # Base confidence from source count
        source_count_factor = min(len(sources) / 4, 1.0)
        
        # Check for uncertainty phrases
        uncertainty_phrases = [
            "i don't have enough information",
            "cannot find information", 
            "i don't know",
            "unclear from the context",
            "might be", "possibly", "perhaps",
            "it appears", "seems to"
        ]
        
        uncertainty_penalty = 0.0
        answer_lower = answer.lower()
        for phrase in uncertainty_phrases:
            if phrase in answer_lower:
                uncertainty_penalty += 0.2
                break
        
        # Source diversity bonus
        unique_files = len(set(doc.metadata.get('source_file', '') for doc in sources))
        diversity_bonus = min(unique_files / 3, 0.2)
        
        # Answer length factor (very short answers might be incomplete)
        length_factor = 0.0
        if len(answer.split()) > 20:
            length_factor = 0.1
        elif len(answer.split()) > 50:
            length_factor = 0.2
        
        # Calculate final confidence
        confidence = (0.4 + source_count_factor * 0.3 + diversity_bonus + length_factor) - uncertainty_penalty
        return max(0.1, min(1.0, confidence))
    
    def get_processing_notes(self, answer: str, sources: List) -> List[str]:
        """Generate processing notes for transparency"""
        notes = []
        
        if len(sources) < 2:
            notes.append("Limited source material - consider adding more relevant documents")
        
        answer_lower = answer.lower()
        if any(phrase in answer_lower for phrase in ["don't have enough information", "cannot find information"]):
            notes.append("Answer indicates insufficient information in knowledge base")
        
        source_files = [doc.metadata.get('source_file', '') for doc in sources]
        unique_sources = set(source_files)
        
        if len(unique_sources) == 1:
            notes.append("Answer based on single document - cross-reference recommended")
        elif len(unique_sources) >= 3:
            notes.append("Answer synthesized from multiple sources")
        
        # Check content types
        content_types = [doc.metadata.get('content_type', 'general') for doc in sources]
        if 'summary' in content_types:
            notes.append("Includes information from summary documents")
        
        return notes
    
    def create_conversational_chain(self):
        """Create a chain that maintains conversation context"""
        try:
            from langchain.chains import ConversationalRetrievalChain
            from langchain.memory import ConversationBufferWindowMemory
            
            memory = ConversationBufferWindowMemory(
                memory_key="chat_history",
                return_messages=True,
                k=5  # Keep last 5 exchanges
            )
            
            # Use custom retriever if available
            retriever = self.custom_retriever if self.custom_retriever else self.vectorstore.as_retriever(
                search_kwargs={"k": 4}
            )
            
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                memory=memory,
                return_source_documents=True,
                verbose=False
            )
            
            return qa_chain
            
        except ImportError:
            print("⚠️  Conversational features not available. Using standard chain.")
            return self.create_chain()
    
    def create_chain_with_custom_retriever(self, retriever):
        """Create chain with a specific retriever"""
        prompt = self.create_advanced_prompt()
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
        
        return qa_chain