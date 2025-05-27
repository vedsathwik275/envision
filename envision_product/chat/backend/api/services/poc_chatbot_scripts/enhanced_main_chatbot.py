# fixed_main_enhanced_chatbot.py
import os
import sys
from dotenv import load_dotenv
from typing import Optional, Dict, List, Any # Added Dict, List, Any
from collections import Counter # Added Counter for file types
from pathlib import Path # Added Path

# Import your existing classes
from .knowledge_base_manager import KnowledgeBaseManager

# Import enhanced classes (make sure file names match exactly)
try:
    from .enhanced_dp import EnhancedDocumentProcessor
except ImportError:
    print("❌ Could not import EnhancedDocumentProcessor from enhanced_dp.py")
    print("Make sure the file enhanced_dp.py exists and contains the EnhancedDocumentProcessor class")
    sys.exit(1)

try:
    from .enhanced_vs import AdvancedVectorStoreManager
except ImportError:
    print("❌ Could not import AdvancedVectorStoreManager from enhanced_vs.py")
    print("Make sure the file enhanced_vs.py exists and contains the AdvancedVectorStoreManager class")
    sys.exit(1)

try:
    from .enhanced_rc import EnhancedRAGChain
except ImportError:
    print("❌ Could not import EnhancedRAGChain from enhanced_rc.py")
    print("Make sure the file enhanced_rc.py exists and contains the EnhancedRAGChain class")
    sys.exit(1)

class FixedEnhancedRAGChatbot:
    def __init__(self, base_kb_manager_directory: Optional[str] = None):
        load_dotenv()
        
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("Please set your OPENAI_API_KEY in the .env file")
        
        if base_kb_manager_directory:
            self.kb_manager = KnowledgeBaseManager(base_directory=base_kb_manager_directory)
        else:
            print("⚠️ WARNING: FixedEnhancedRAGChatbot initialized without explicit base_kb_manager_directory. Using KBM default.")
            self.kb_manager = KnowledgeBaseManager() 
        
        self.qa_chain = None
        self.current_kb = None
        self.conversation_history = [] # Not used by API currently but part of original class
    
    def setup_enhanced_knowledge_base(self, kb_name: str, retriever_type: str ="hybrid") -> bool:
        """Setup knowledge base with enhanced processing"""
        try:
            documents_path = self.kb_manager.get_documents_path(kb_name)
            vector_store_path = self.kb_manager.get_vector_store_path(kb_name)
            
            print(f"🔄 Setting up enhanced knowledge base: {kb_name} (KBM base: {self.kb_manager.base_directory})")
            
            processor = EnhancedDocumentProcessor(
                documents_path, 
                chunk_size=1000, 
                chunk_overlap=200
            )
            
            # Get document files and basic info before loading all content
            try:
                document_files = processor.get_document_files()
            except FileNotFoundError:
                print(f"❌ Documents folder not found: {documents_path}")
                return False
            except ValueError as ve: # Catches "No supported documents found"
                print(f"❌ {str(ve)}")
                return False

            total_files = len(document_files)
            if total_files == 0:
                print(f"❌ No supported documents found in {documents_path}. Ensure files have supported extensions.")
                return False
            
            file_type_counts: Dict[str, int] = Counter(Path(f).suffix.lower() for f in document_files)
            file_types_str = ", ".join([f"{ext}: {count}" for ext, count in file_type_counts.items()])
            
            print(f"📊 Initial Knowledge Base Scan:")
            print(f"   📁 Folder: {documents_path}")
            print(f"   📄 Total supported files found: {total_files}")
            print(f"   📋 File types detected: {file_types_str}")
            
            # Process documents with enhancements
            print("\n🔄 Processing documents with enhanced features (loading, splitting, metadata)...")
            try:
                texts = processor.load_and_split_folder_enhanced()
            except ValueError as ve: # Catches "No documents could be loaded successfully"
                print(f"❌ Error during document loading/splitting: {str(ve)}")
                # Potentially update metadata to an error state here if desired via self.kb_manager
                return False
            
            # Analyze quality (using the already loaded texts)
            quality_metrics = processor.analyze_knowledge_base_quality(texts)
            print(f"\n📈 Quality Metrics Post-Processing:")
            print(f"   📊 Total chunks created: {quality_metrics.get('total_chunks', 0)}")
            print(f"   📏 Avg chunk size: {quality_metrics.get('average_chunk_size', 0):.0f} chars")
            print(f"   📚 Unique source files processed: {quality_metrics.get('unique_source_files', 0)}")
            
            # Display file type distribution from quality_metrics if available
            file_type_dist = quality_metrics.get('file_type_distribution')
            if file_type_dist:
                dist_str = ", ".join([f"{ext}: {count}" for ext, count in file_type_dist.items()])
                print(f"   📋 Processed file types (from chunks): {dist_str}")

            if quality_metrics.get('recommendations'):
                print(f"   💡 Recommendations:")
                for rec in quality_metrics['recommendations']:
                    print(f"      • {rec}")
            
            # Create advanced vector store
            print(f"\n🧠 Creating advanced vector store at {vector_store_path}...")
            vector_manager = AdvancedVectorStoreManager(persist_directory=vector_store_path)
            vectorstore = vector_manager.create_vectorstore_with_metadata(texts)
            
            # Create advanced retriever
            print(f"🔍 Setting up {retriever_type} retriever (and persisting BM25 if applicable)...")
            retriever = vector_manager.create_advanced_retriever(
                vectorstore, 
                texts, # Pass the loaded texts for BM25 creation
                retriever_type=retriever_type,
                persist_bm25_if_creating=True # IMPORTANT: Tell it to save BM25
            )
            
            # Create enhanced RAG chain with proper initialization
            print(f"⚡ Creating enhanced RAG chain...")
            rag_chain = EnhancedRAGChain(vectorstore, retriever=retriever)
            self.qa_chain = rag_chain.create_advanced_chain()
            self.current_kb = kb_name
            
            # Update metadata using its own kb_manager.
            # KBService will call its own kb_manager.update_metadata to set status='ready' AFTER this returns.
            self.kb_manager.update_metadata(
                kb_name,
                document_count=quality_metrics.get('unique_source_files', total_files), # Use processed unique files, fallback to initial scan
                chunk_count=quality_metrics.get('total_chunks', 0),
                retriever_type=retriever_type,
                quality_score=self.calculate_quality_score(quality_metrics)
            )
            
            print(f"✅ Enhanced knowledge base '{kb_name}' processing by chatbot script finished!")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up enhanced knowledge base in chatbot script: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_existing_enhanced_kb(self, kb_name: str) -> bool:
        """Load existing knowledge base with enhanced features"""
        try:
            vector_store_path = self.kb_manager.get_vector_store_path(kb_name)
            print(f"🔄 Loading existing knowledge base: {kb_name} (KBM base: {self.kb_manager.base_directory}, VS base: {vector_store_path})")
            
            vector_manager = AdvancedVectorStoreManager(persist_directory=vector_store_path)
            vectorstore = vector_manager.load_vectorstore()
            
            if vectorstore:
                kb_list = self.kb_manager.list_knowledge_bases()
                kb_metadata = next((kb for kb in kb_list if kb.get('name') == kb_name), {})
                retriever_type = kb_metadata.get('retriever_type', 'standard')
                
                print(f"🔍 Loading retriever type '{retriever_type}' (expecting persisted BM25 if hybrid)...")
                retriever = vector_manager.create_advanced_retriever(
                    vectorstore, 
                    texts=None, # IMPORTANT: No texts, expect BM25 to load from pickle
                    retriever_type=retriever_type,
                    persist_bm25_if_creating=False # IMPORTANT: Not creating/persisting here
                )
                
                if not retriever:
                    print(f"❌ Failed to create/load retriever for KB '{kb_name}'.")
                    return False

                print(f"⚡ Creating enhanced RAG chain for loaded KB...")
                rag_chain = EnhancedRAGChain(vectorstore, retriever=retriever)
                self.qa_chain = rag_chain.create_advanced_chain()
                self.current_kb = kb_name
                
                print(f"✅ Loaded enhanced knowledge base: {kb_name}")
                return True
            else:
                print(f"❌ No (Chroma) vector store found for: {kb_name} at {vector_store_path}")
                return False
                
        except Exception as e:
            print(f"❌ Error loading knowledge base in chatbot script: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def calculate_quality_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall quality score"""
        if not metrics: return 0.0 # Handle empty metrics
        score = 0.5  # Base score
        if metrics.get('total_chunks', 0) > 50: score += 0.2
        elif metrics.get('total_chunks', 0) > 20: score += 0.1
        avg_size = metrics.get('average_chunk_size', 0)
        if 500 <= avg_size <= 1500: score += 0.2
        if metrics.get('unique_source_files', 0) > 3: score += 0.1
        return min(1.0, round(score, 2))
    
    def interactive_setup(self) -> bool:
        """Enhanced interactive setup"""
        print("\n🚀 Enhanced RAG Chatbot - Setup")
        print("=" * 60)
        knowledge_bases = self.kb_manager.list_knowledge_bases()
        if knowledge_bases:
            print("\n📚 Available Knowledge Bases:")
            for i, kb in enumerate(knowledge_bases, 1):
                quality = kb.get('quality_score', 0.0)
                retriever = kb.get('retriever_type', 'standard')
                quality_emoji = "🟢" if quality > 0.7 else "🟡" if quality > 0.5 else "🔴"
                print(f"   {i}. {kb['name']} {quality_emoji}")
                print(f"      📊 {kb.get('document_count', 0)} docs, {kb.get('chunk_count', 0)} chunks")
                print(f"      🔍 {retriever} retriever, Quality: {quality:.1%}")
        print("\n🔧 Options:")
        print("1. Create new knowledge base")
        print("2. Load existing knowledge base")  
        print("3. Process/reprocess with enhancements")
        print("4. Exit")
        choice = input("\nSelect option (1-4): ").strip()
        if choice == "1": return self.create_new_kb()
        elif choice == "2": return self.select_existing_kb()
        elif choice == "3": return self.reprocess_with_enhancements()
        elif choice == "4": print("👋 Goodbye!"); return False
        else: print("❌ Invalid choice."); return self.interactive_setup()
    
    def create_new_kb(self) -> bool:
        """Create new knowledge base"""
        name = input("Enter knowledge base name: ").strip()
        if not name: print("❌ Name cannot be empty"); return False
        description = input("Enter description (optional): ").strip()
        try:
            kb_path = self.kb_manager.create_knowledge_base(name, description)
            print(f"\n📁 Knowledge base created! Add documents to: {os.path.join(kb_path, 'documents')}")
            print("📝 Then run again to process with enhancements.")
            return False # Returns False to indicate setup is not complete for chat
        except ValueError as e: print(f"❌ {str(e)}"); return False
    
    def select_existing_kb(self) -> bool:
        """Select and load existing knowledge base"""
        knowledge_bases = self.kb_manager.list_knowledge_bases()
        if not knowledge_bases: print("❌ No knowledge bases found."); return False
        print("\n📚 Select Knowledge Base:")
        for i, kb in enumerate(knowledge_bases, 1): print(f"   {i}. {kb['name']}")
        try:
            choice = int(input("Enter number: ").strip())
            if 1 <= choice <= len(knowledge_bases):
                return self.load_existing_enhanced_kb(knowledge_bases[choice - 1]['name'])
            else: print("❌ Invalid choice"); return False
        except ValueError: print("❌ Please enter a valid number"); return False
    
    def reprocess_with_enhancements(self) -> bool:
        """Reprocess existing KB with enhancements"""
        knowledge_bases = self.kb_manager.list_knowledge_bases()
        if not knowledge_bases: print("❌ No knowledge bases found."); return False
        print("\n📚 Select Knowledge Base to Enhance:")
        for i, kb in enumerate(knowledge_bases, 1): print(f"   {i}. {kb['name']}")
        try:
            choice = int(input("Enter number: ").strip())
            if 1 <= choice <= len(knowledge_bases):
                kb_name = knowledge_bases[choice - 1]['name']
                print("\n🔍 Select Retriever Type:")
                print("1. Hybrid (Vector + BM25) - Recommended")
                print("2. Multi-query (Query expansion)")
                print("3. Advanced hybrid (All features)")
                print("4. Standard (Vector only)")
                retriever_choice = input("Select (1-4, default=1): ").strip() or "1"
                retriever_map = {"1": "hybrid", "2": "multi_query", "3": "advanced_hybrid", "4": "standard"}
                retriever_type = retriever_map.get(retriever_choice, "hybrid")
                return self.setup_enhanced_knowledge_base(kb_name, retriever_type)
            else: print("❌ Invalid choice"); return False
        except ValueError: print("❌ Please enter a valid number"); return False
    
    def get_enhanced_response(self, question: str) -> Dict[str, Any]:
        """Get enhanced response. Returns dict for ChatService compatibility."""
        if not self.qa_chain:
            return {
                "answer": "No knowledge base loaded or QA chain not initialized. Please setup/load a knowledge base first.",
                "confidence": 0.0, # Matched key for ChatService
                "sources": [],
                "debug_info": {"error": "QA chain not available"}
            }
        
        try:
            result = self.qa_chain({"query": question})
            
            formatted_answer_str = self.format_enhanced_response_for_display(result, question)
            
            confidence_score = result.get('confidence_score', 0.0) # Ensure float for Pydantic
            sources_list = result.get('source_documents', []) 
            
            api_sources = []
            if sources_list:
                for src_doc in sources_list:
                    # Ensure metadata is a flat dict of str:str or str:primitive for JSON serialization
                    simple_metadata = {k: str(v) for k, v in src_doc.metadata.items()} if src_doc.metadata else {}
                    api_sources.append({
                        "page_content": str(src_doc.page_content),
                        "metadata": simple_metadata
                    })
            
            # Prepare debug_info, ensuring it's serializable
            debug_info_payload = {}
            if result.get('metadata'): # example from previous version of this method
                debug_info_payload = {k: str(v) for k, v in result.get('metadata').items()} 
            # Add more details if useful, e.g., retriever type, query transformation details
            debug_info_payload['retriever_type_used'] = self.qa_chain.retriever.__class__.__name__ if hasattr(self.qa_chain, 'retriever') and self.qa_chain.retriever else 'unknown'

            return {
                "answer": formatted_answer_str, # For API, this is the primary human-readable answer text
                "confidence": float(confidence_score), # Ensure it's a float
                "sources": api_sources,
                "debug_info": debug_info_payload
            }
            
        except Exception as e:
            return {
                "answer": f"Error processing question: {str(e)}",
                "confidence": 0.0,
                "sources": [],
                "debug_info": {"error": str(e), "traceback": traceback.format_exc() if os.getenv("DEBUG_MODE") else "Traceback hidden"}
            }
    
    def format_enhanced_response_for_display(self, result: dict, question: str) -> str:
        """Format the response with enhancements (for terminal/display)."""
        answer = result.get('result', result.get('answer', 'No answer provided'))
        confidence = result.get('confidence_score', 0.5)
        sources = result.get('source_documents', [])
        response_parts = []
        confidence_emoji = self.get_confidence_emoji(confidence)
        response_parts.append(f"{confidence_emoji} **Answer** (Confidence: {confidence:.1%})")
        response_parts.append(str(answer)) # Ensure answer is string
        response_parts.append("")
        if sources:
            response_parts.append("📚 **Sources**")
            for i, doc in enumerate(sources[:3], 1):
                source_file = doc.metadata.get('source_file', f'Source {i}')
                preview = str(doc.page_content)[:150] + "..." if len(str(doc.page_content)) > 150 else str(doc.page_content)
                response_parts.append(f"   {i}. {source_file}")
                response_parts.append(f"      └─ {preview}")
            response_parts.append("")
        if result.get('metadata', {}).get('processing_notes'):
            response_parts.append("💡 **Notes**")
            for note in result['metadata']['processing_notes']:
                response_parts.append(f"   • {note}")
            response_parts.append("")
        return "\n".join(response_parts)
    
    def get_confidence_emoji(self, confidence: float) -> str:
        """Get emoji based on confidence level"""
        if confidence >= 0.8: return "🎯"
        elif confidence >= 0.6: return "✅"
        elif confidence >= 0.4: return "⚠️"
        else: return "❓"
    
    def enhanced_chat(self):
        """Enhanced chat session (for terminal use)"""
        if not self.qa_chain: print("❌ No knowledge base loaded."); return
        print(f"\n🚀 Enhanced RAG Chatbot - Knowledge Base: {self.current_kb}")
        print("=" * 70)
        print("💡 Ask questions about your documents")
        print("💡 I'll provide detailed answers with confidence levels and sources")
        print("💡 Type 'quit', 'exit', or 'bye' to end")
        print("=" * 70 + "\n")
        while True:
            try:
                user_input = input("🧑 You: ").strip()
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']: print("👋 Goodbye! Thanks for chatting!"); break
                if not user_input: print("❓ Please enter a question."); continue
                print("\n🔍 Analyzing your question...")
                response_dict = self.get_enhanced_response(user_input) 
                print(f"\n{response_dict.get('answer', 'Error retrieving formatted answer.')}\n") # Display the formatted string answer
                print("═" * 70)
            except KeyboardInterrupt: print("\n\n👋 Session interrupted. Goodbye!"); break
            except Exception as e: print(f"\n❌ An error occurred: {str(e)}\n")

def main(): # For standalone script execution
    """Main function to run enhanced chatbot (standalone)."""
    try:
        print("🚀 Starting Enhanced RAG Chatbot (Standalone Mode)...")
        # When run standalone, it uses its default KBM path unless a mechanism to override is added.
        chatbot = FixedEnhancedRAGChatbot() 
        if chatbot.interactive_setup():
            chatbot.enhanced_chat()
    except Exception as e:
        print(f"❌ Failed to initialize enhanced chatbot: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()