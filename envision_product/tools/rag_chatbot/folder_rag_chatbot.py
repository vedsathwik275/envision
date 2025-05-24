import os
import sys
from dotenv import load_dotenv
from document_processor import FolderDocumentProcessor
from vector_store import VectorStoreManager
from rag_chain import RAGChain
from knowledge_base_manager import KnowledgeBaseManager

class FolderRAGChatbot:
    def __init__(self):
        load_dotenv()
        
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("Please set your OPENAI_API_KEY in the .env file")
        
        self.kb_manager = KnowledgeBaseManager()
        self.qa_chain = None
        self.current_kb = None
    
    def setup_knowledge_base_from_folder(self, kb_name):
        """Setup knowledge base from documents folder"""
        try:
            documents_path = self.kb_manager.get_documents_path(kb_name)
            vector_store_path = self.kb_manager.get_vector_store_path(kb_name)
            
            # Check if documents exist
            processor = FolderDocumentProcessor(documents_path)
            kb_info = processor.get_knowledge_base_info()
            
            if kb_info['total_files'] == 0:
                print(f"❌ No documents found in {documents_path}")
                print("Please add documents to the folder before processing.")
                return False
            
            print(f"📊 Knowledge Base Info:")
            print(f"   📁 Folder: {documents_path}")
            print(f"   📄 Total files: {kb_info['total_files']}")
            print(f"   📋 File types: {kb_info['file_types']}")
            
            # Process documents
            print("\n🔄 Processing documents...")
            texts = processor.load_and_split_folder()
            
            # Create vector store
            vector_manager = VectorStoreManager(vector_store_path)
            vectorstore = vector_manager.create_vectorstore(texts)
            
            # Create RAG chain
            rag_chain = RAGChain(vectorstore)
            self.qa_chain = rag_chain.create_chain()
            self.current_kb = kb_name
            
            # Update metadata
            self.kb_manager.update_metadata(
                kb_name,
                document_count=kb_info['total_files'],
                chunk_count=len(texts)
            )
            
            print(f"✅ Knowledge base '{kb_name}' is ready!")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up knowledge base: {str(e)}")
            return False
    
    def load_existing_knowledge_base(self, kb_name):
        """Load existing processed knowledge base"""
        try:
            vector_store_path = self.kb_manager.get_vector_store_path(kb_name)
            
            vector_manager = VectorStoreManager(vector_store_path)
            vectorstore = vector_manager.load_vectorstore()
            
            if vectorstore:
                rag_chain = RAGChain(vectorstore)
                self.qa_chain = rag_chain.create_chain()
                self.current_kb = kb_name
                print(f"✅ Loaded existing knowledge base: {kb_name}")
                return True
            else:
                print(f"❌ No processed knowledge base found for: {kb_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error loading knowledge base: {str(e)}")
            return False
    
    def interactive_setup(self):
        """Interactive setup for knowledge base selection"""
        print("\n🚀 RAG Chatbot - Knowledge Base Setup")
        print("=" * 50)
        
        # List existing knowledge bases
        knowledge_bases = self.kb_manager.list_knowledge_bases()
        
        if knowledge_bases:
            print("\n📚 Available Knowledge Bases:")
            for i, kb in enumerate(knowledge_bases, 1):
                print(f"   {i}. {kb['name']} ({kb['document_count']} docs, {kb['chunk_count']} chunks)")
        
        print("\n🔧 Options:")
        print("1. Create new knowledge base")
        print("2. Use existing knowledge base")
        print("3. Process documents in existing knowledge base")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            return self.create_new_knowledge_base()
        elif choice == "2":
            return self.select_existing_knowledge_base()
        elif choice == "3":
            return self.process_existing_knowledge_base()
        elif choice == "4":
            print("👋 Goodbye!")
            return False
        else:
            print("❌ Invalid choice. Please try again.")
            return self.interactive_setup()
    
    def create_new_knowledge_base(self):
        """Create a new knowledge base"""
        name = input("Enter knowledge base name: ").strip()
        if not name:
            print("❌ Name cannot be empty")
            return False
        
        description = input("Enter description (optional): ").strip()
        
        try:
            kb_path = self.kb_manager.create_knowledge_base(name, description)
            documents_path = os.path.join(kb_path, "documents")
            
            print(f"\n📁 Knowledge base created!")
            print(f"📄 Add your documents to: {documents_path}")
            print("📝 Then run the chatbot again to process them.")
            
            return False
            
        except ValueError as e:
            print(f"❌ {str(e)}")
            return False
    
    def select_existing_knowledge_base(self):
        """Select and load existing knowledge base"""
        knowledge_bases = self.kb_manager.list_knowledge_bases()
        
        if not knowledge_bases:
            print("❌ No knowledge bases found. Create one first.")
            return False
        
        print("\n📚 Select Knowledge Base:")
        for i, kb in enumerate(knowledge_bases, 1):
            print(f"   {i}. {kb['name']}")
        
        try:
            choice = int(input("Enter number: ").strip())
            if 1 <= choice <= len(knowledge_bases):
                kb_name = knowledge_bases[choice - 1]['name']
                return self.load_existing_knowledge_base(kb_name)
            else:
                print("❌ Invalid choice")
                return False
        except ValueError:
            print("❌ Please enter a valid number")
            return False
    
    def process_existing_knowledge_base(self):
        """Process documents in existing knowledge base"""
        knowledge_bases = self.kb_manager.list_knowledge_bases()
        
        if not knowledge_bases:
            print("❌ No knowledge bases found. Create one first.")
            return False
        
        print("\n📚 Select Knowledge Base to Process:")
        for i, kb in enumerate(knowledge_bases, 1):
            print(f"   {i}. {kb['name']}")
        
        try:
            choice = int(input("Enter number: ").strip())
            if 1 <= choice <= len(knowledge_bases):
                kb_name = knowledge_bases[choice - 1]['name']
                return self.setup_knowledge_base_from_folder(kb_name)
            else:
                print("❌ Invalid choice")
                return False
        except ValueError:
            print("❌ Please enter a valid number")
            return False
    
    def get_response(self, question):
        """Get response from the RAG chatbot"""
        if not self.qa_chain:
            return "❌ No knowledge base loaded. Please setup a knowledge base first."
        
        try:
            result = self.qa_chain({"query": question})
            answer = result['result']
            sources = result.get('source_documents', [])
            
            response = f"🤖 {answer}\n"
            
            if sources:
                response += "\n📖 Sources:\n"
                seen_sources = set()
                for i, doc in enumerate(sources[:3], 1):
                    source_file = doc.metadata.get('source_file', 'Unknown')
                    if source_file not in seen_sources:
                        preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
                        response += f"   {i}. {source_file}: {preview}\n"
                        seen_sources.add(source_file)
            
            return response
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def chat(self):
        """Start the interactive chat session"""
        if not self.qa_chain:
            print("❌ No knowledge base loaded.")
            return
        
        print(f"\n🚀 RAG Chatbot - Knowledge Base: {self.current_kb}")
        print("=" * 60)
        print("💡 Ask questions about your documents")
        print("💡 Type 'quit', 'exit', or 'bye' to end the session")
        print("=" * 60 + "\n")
        
        while True:
            try:
                user_input = input("🧑 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("👋 Goodbye! Thanks for chatting!")
                    break
                
                if not user_input:
                    print("❓ Please enter a question.")
                    continue
                
                print("\n🔍 Searching knowledge base...")
                response = self.get_response(user_input)
                print(f"\n{response}\n")
                print("-" * 60)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thanks for chatting!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {str(e)}\n")

def main():
    try:
        chatbot = FolderRAGChatbot()
        
        # Interactive setup
        if chatbot.interactive_setup():
            chatbot.chat()
            
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {str(e)}")

if __name__ == "__main__":
    main()
