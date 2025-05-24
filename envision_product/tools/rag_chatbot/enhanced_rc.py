from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import BaseRetriever
from typing import List, Dict, Any, Optional
import os

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
        
    def create_advanced_prompt(self):
        """Create a more sophisticated prompt template"""
        template = """You are an expert assistant analyzing documents to provide accurate, comprehensive answers.

INSTRUCTIONS:
- Answer based ONLY on the provided context
- Be specific and detailed when information is available
- If information is incomplete, acknowledge what you know and what's missing
- Structure your response clearly with main points
- Use examples and quotes from the context when relevant
- If no relevant information exists, clearly state "I cannot find information about this topic in the provided documents"

CONTEXT:
{context}

QUESTION: {question}

DETAILED ANALYSIS:
Let me examine the relevant information from the documents to provide you with a comprehensive answer:

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
                search_kwargs={"k": 4, "fetch_k": 10}
            )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
        
        return qa_chain
    
    def create_advanced_chain(self):
        """Create advanced chain with post-processing"""
        base_chain = self.create_chain()
        
        # Wrap the chain to add post-processing
        class EnhancedChain:
            def __init__(self, base_chain, processor):
                self.base_chain = base_chain
                self.processor = processor
            
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
        
        return {
            'result': answer,  # Keep original key for compatibility
            'answer': answer,  # Also provide as 'answer'
            'source_documents': sources,  # Keep original
            'sources': processed_sources,  # Enhanced sources
            'source_diversity': {
                'unique_files': len(source_files),
                'file_types': list(source_types)
            },
            'confidence_score': confidence_score,
            'metadata': {
                'total_sources_found': len(sources),
                'processing_notes': self.get_processing_notes(answer, sources)
            }
        }
    
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