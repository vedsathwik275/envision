# fixed_main_enhanced_chatbot.py
import os
import sys
from dotenv import load_dotenv

# Import your existing classes
from knowledge_base_manager import KnowledgeBaseManager

# Import enhanced classes (make sure file names match exactly)
try:
    from enhanced_dp import EnhancedDocumentProcessor
except ImportError:
    print("❌ Could not import EnhancedDocumentProcessor from enhanced_dp.py")
    print("Make sure the file enhanced_dp.py exists and contains the EnhancedDocumentProcessor class")
    sys.exit(1)

try:
    from enhanced_vs import AdvancedVectorStoreManager
except ImportError:
    print("❌ Could not import AdvancedVectorStoreManager from enhanced_vs.py")
    print("Make sure the file enhanced_vs.py exists and contains the AdvancedVectorStoreManager class")
    sys.exit(1)

try:
    from enhanced_rc import EnhancedRAGChain
except ImportError:
    print("❌ Could not import EnhancedRAGChain from enhanced_rc.py")
    print("Make sure the file enhanced_rc.py exists and contains the EnhancedRAGChain class")
    sys.exit(1)

class FixedEnhancedRAGChatbot:
    def __init__(self):
        load_dotenv()
        
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("Please set your OPENAI_API_KEY in the .env file")
        
        self.kb_manager = KnowledgeBaseManager()
        self.qa_chain = None
        self.current_kb = None
        self.conversation_history = []
    
    def setup_enhanced_knowledge_base(self, kb_name, retriever_type="hybrid"):
        """Setup knowledge base with enhanced processing"""
        try:
            documents_path = self.kb_manager.get_documents_path(kb_name)
            vector_store_path = self.kb_manager.get_vector_store_path(kb_name)
            
            print(f"🔄 Setting up enhanced knowledge base: {kb_name}")
            
            # Enhanced document processing
            processor = EnhancedDocumentProcessor(
                documents_path, 
                chunk_size=1000, 
                chunk_overlap=200
            )
            
            # Check documents
            kb_info = processor.get_knowledge_base_info()
            if kb_info['total_files'] == 0:
                print(f"❌ No documents found in {documents_path}")
                return False
            
            print(f"📊 Knowledge Base Analysis:")
            print(f"   📁 Folder: {documents_path}")
            print(f"   📄 Files: {kb_info['total_files']}")
            print(f"   📋 Types: {kb_info['file_types']}")
            
            # Process documents with enhancements
            print("\n🔄 Processing documents with enhanced features...")
            texts = processor.load_and_split_folder_enhanced()
            
            # Analyze quality
            quality_metrics = processor.analyze_knowledge_base_quality(texts)
            print(f"\n📈 Quality Metrics:")
            print(f"   📊 Total chunks: {quality_metrics['total_chunks']}")
            print(f"   📏 Avg chunk size: {quality_metrics['average_chunk_size']:.0f} chars")
            print(f"   📚 Unique files: {quality_metrics['unique_source_files']}")
            
            if quality_metrics.get('recommendations'):
                print(f"   💡 Recommendations:")
                for rec in quality_metrics['recommendations']:
                    print(f"      • {rec}")
            
            # Create advanced vector store
            print(f"\n🧠 Creating advanced vector store...")
            vector_manager = AdvancedVectorStoreManager(vector_store_path)
            vectorstore = vector_manager.create_vectorstore_with_metadata(texts)
            
            # Create advanced retriever
            print(f"🔍 Setting up {retriever_type} retriever...")
            retriever = vector_manager.create_advanced_retriever(
                vectorstore, texts, retriever_type
            )
            
            # Create enhanced RAG chain with proper initialization
            print(f"⚡ Creating enhanced RAG chain...")
            rag_chain = EnhancedRAGChain(vectorstore, retriever=retriever)
            self.qa_chain = rag_chain.create_advanced_chain()
            self.current_kb = kb_name
            
            # Update metadata
            self.kb_manager.update_metadata(
                kb_name,
                document_count=kb_info['total_files'],
                chunk_count=len(texts),
                retriever_type=retriever_type,
                quality_score=self.calculate_quality_score(quality_metrics)
            )
            
            print(f"✅ Enhanced knowledge base '{kb_name}' is ready!")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up enhanced knowledge base: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_existing_enhanced_kb(self, kb_name):
        """Load existing knowledge base with enhanced features"""
        try:
            vector_store_path = self.kb_manager.get_vector_store_path(kb_name)
            
            # Load vector store
            vector_manager = AdvancedVectorStoreManager(vector_store_path)
            vectorstore = vector_manager.load_vectorstore()
            
            if vectorstore:
                # Get KB metadata for retriever type
                kb_list = self.kb_manager.list_knowledge_bases()
                kb_metadata = next((kb for kb in kb_list if kb['name'] == kb_name), {})
                retriever_type = kb_metadata.get('retriever_type', 'standard')
                
                print(f"🔍 Loading with {retriever_type} retriever...")
                
                # Create retriever (pass empty list for texts since we're loading existing)
                retriever = vector_manager.create_advanced_retriever(
                    vectorstore, [], retriever_type
                )
                
                # Create enhanced RAG chain
                rag_chain = EnhancedRAGChain(vectorstore, retriever=retriever)
                self.qa_chain = rag_chain.create_advanced_chain()
                self.current_kb = kb_name
                
                print(f"✅ Loaded enhanced knowledge base: {kb_name}")
                return True
            else:
                print(f"❌ No processed knowledge base found for: {kb_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error loading knowledge base: {str(e)}")
            return False
    
    def calculate_quality_score(self, metrics):
        """Calculate overall quality score"""
        score = 0.5  # Base score
        
        # More chunks = better coverage
        if metrics['total_chunks'] > 50:
            score += 0.2
        elif metrics['total_chunks'] > 20:
            score += 0.1
        
        # Good chunk size range
        avg_size = metrics['average_chunk_size']
        if 500 <= avg_size <= 1500:
            score += 0.2
        
        # Source diversity
        if metrics['unique_source_files'] > 3:
            score += 0.1
        
        return min(1.0, score)
    
    def interactive_setup(self):
        """Enhanced interactive setup"""
        print("\n🚀 Enhanced RAG Chatbot - Setup")
        print("=" * 60)
        
        # Show existing knowledge bases
        knowledge_bases = self.kb_manager.list_knowledge_bases()
        
        if knowledge_bases:
            print("\n📚 Available Knowledge Bases:")
            for i, kb in enumerate(knowledge_bases, 1):
                quality = kb.get('quality_score', 0.5)
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
        
        if choice == "1":
            return self.create_new_kb()
        elif choice == "2":
            return self.select_existing_kb()
        elif choice == "3":
            return self.reprocess_with_enhancements()
        elif choice == "4":
            print("👋 Goodbye!")
            return False
        else:
            print("❌ Invalid choice.")
            return self.interactive_setup()
    
    def create_new_kb(self):
        """Create new knowledge base"""
        name = input("Enter knowledge base name: ").strip()
        if not name:
            print("❌ Name cannot be empty")
            return False
        
        description = input("Enter description (optional): ").strip()
        
        try:
            kb_path = self.kb_manager.create_knowledge_base(name, description)
            documents_path = os.path.join(kb_path, "documents")
            
            print(f"\n📁 Knowledge base created!")
            print(f"📄 Add documents to: {documents_path}")
            print("📝 Then run again to process with enhancements.")
            return False
            
        except ValueError as e:
            print(f"❌ {str(e)}")
            return False
    
    def select_existing_kb(self):
        """Select and load existing knowledge base"""
        knowledge_bases = self.kb_manager.list_knowledge_bases()
        if not knowledge_bases:
            print("❌ No knowledge bases found.")
            return False
        
        print("\n📚 Select Knowledge Base:")
        for i, kb in enumerate(knowledge_bases, 1):
            print(f"   {i}. {kb['name']}")
        
        try:
            choice = int(input("Enter number: ").strip())
            if 1 <= choice <= len(knowledge_bases):
                kb_name = knowledge_bases[choice - 1]['name']
                return self.load_existing_enhanced_kb(kb_name)
            else:
                print("❌ Invalid choice")
                return False
        except ValueError:
            print("❌ Please enter a valid number")
            return False
    
    def reprocess_with_enhancements(self):
        """Reprocess existing KB with enhancements"""
        knowledge_bases = self.kb_manager.list_knowledge_bases()
        if not knowledge_bases:
            print("❌ No knowledge bases found.")
            return False
        
        print("\n📚 Select Knowledge Base to Enhance:")
        for i, kb in enumerate(knowledge_bases, 1):
            print(f"   {i}. {kb['name']}")
        
        try:
            choice = int(input("Enter number: ").strip())
            if 1 <= choice <= len(knowledge_bases):
                kb_name = knowledge_bases[choice - 1]['name']
                
                # Select retriever type
                print("\n🔍 Select Retriever Type:")
                print("1. Hybrid (Vector + BM25) - Recommended")
                print("2. Multi-query (Query expansion)")
                print("3. Advanced hybrid (All features)")
                print("4. Standard (Vector only)")
                
                retriever_choice = input("Select (1-4, default=1): ").strip() or "1"
                retriever_map = {
                    "1": "hybrid",
                    "2": "multi_query", 
                    "3": "advanced_hybrid",
                    "4": "standard"
                }
                
                retriever_type = retriever_map.get(retriever_choice, "hybrid")
                return self.setup_enhanced_knowledge_base(kb_name, retriever_type)
            else:
                print("❌ Invalid choice")
                return False
        except ValueError:
            print("❌ Please enter a valid number")
            return False
    
    def get_enhanced_response(self, question: str) -> str:
        """Get enhanced response"""
        if not self.qa_chain:
            return "❌ No knowledge base loaded. Please setup a knowledge base first."
        
        try:
            # Get the response
            result = self.qa_chain({"query": question})
            
            # Format enhanced response
            return self.format_enhanced_response(result, question)
            
        except Exception as e:
            return f"❌ Error processing question: {str(e)}"
    
    def format_enhanced_response(self, result: dict, question: str) -> str:
        """Format the response with enhancements"""
        answer = result.get('result', result.get('answer', 'No answer provided'))
        confidence = result.get('confidence_score', 0.5)
        sources = result.get('source_documents', [])
        
        # Build response
        response_parts = []
        
        # Confidence indicator
        confidence_emoji = self.get_confidence_emoji(confidence)
        response_parts.append(f"{confidence_emoji} **Answer** (Confidence: {confidence:.1%})")
        response_parts.append(answer)
        response_parts.append("")
        
        # Sources
        if sources:
            response_parts.append("📚 **Sources**")
            for i, doc in enumerate(sources[:3], 1):
                source_file = doc.metadata.get('source_file', f'Source {i}')
                preview = doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
                response_parts.append(f"   {i}. {source_file}")
                response_parts.append(f"      └─ {preview}")
            response_parts.append("")
        
        # Processing notes
        if result.get('metadata', {}).get('processing_notes'):
            response_parts.append("💡 **Notes**")
            for note in result['metadata']['processing_notes']:
                response_parts.append(f"   • {note}")
            response_parts.append("")
        
        return "\n".join(response_parts)
    
    def get_confidence_emoji(self, confidence: float) -> str:
        """Get emoji based on confidence level"""
        if confidence >= 0.8:
            return "🎯"
        elif confidence >= 0.6:
            return "✅"
        elif confidence >= 0.4:
            return "⚠️"
        else:
            return "❓"
    
    def enhanced_chat(self):
        """Enhanced chat session"""
        if not self.qa_chain:
            print("❌ No knowledge base loaded.")
            return
        
        print(f"\n🚀 Enhanced RAG Chatbot - Knowledge Base: {self.current_kb}")
        print("=" * 70)
        print("💡 Ask questions about your documents")
        print("💡 I'll provide detailed answers with confidence levels and sources")
        print("💡 Type 'quit', 'exit', or 'bye' to end")
        print("=" * 70 + "\n")
        
        while True:
            try:
                user_input = input("🧑 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("👋 Goodbye! Thanks for chatting!")
                    break
                
                if not user_input:
                    print("❓ Please enter a question.")
                    continue
                
                print("\n🔍 Analyzing your question...")
                response = self.get_enhanced_response(user_input)
                print(f"\n{response}\n")
                print("═" * 70)
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {str(e)}\n")

def main():
    """Main function to run enhanced chatbot"""
    try:
        print("🚀 Starting Enhanced RAG Chatbot...")
        chatbot = FixedEnhancedRAGChatbot()
        
        if chatbot.interactive_setup():
            chatbot.enhanced_chat()
            
    except Exception as e:
        print(f"❌ Failed to initialize enhanced chatbot: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()