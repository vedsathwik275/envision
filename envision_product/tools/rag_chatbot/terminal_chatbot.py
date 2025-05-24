import os
from dotenv import load_dotenv
from document_processor import DocumentProcessor
from vector_store import VectorStoreManager
from rag_chain import RAGChain

class TerminalRAGChatbot:
    def __init__(self, knowledge_base_path=None):
        load_dotenv()
        
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("Please set your OPENAI_API_KEY in the .env file")
        
        self.vector_manager = VectorStoreManager()
        self.qa_chain = None
        
        if knowledge_base_path:
            self.setup_knowledge_base(knowledge_base_path)
        else:
            self.load_existing_knowledge_base()
    
    def setup_knowledge_base(self, file_path):
        """Setup knowledge base from document"""
        print(f"📚 Processing document: {file_path}")
        
        processor = DocumentProcessor(file_path)
        texts = processor.load_and_split()
        
        print(f"✂️  Split document into {len(texts)} chunks")
        
        vectorstore = self.vector_manager.create_vectorstore(texts)
        print("🔍 Created vector embeddings")
        
        rag_chain = RAGChain(vectorstore)
        self.qa_chain = rag_chain.create_chain()
        
        print("✅ Knowledge base ready!")
    
    def load_existing_knowledge_base(self):
        """Load existing knowledge base"""
        vectorstore = self.vector_manager.load_vectorstore()
        if vectorstore:
            rag_chain = RAGChain(vectorstore)
            self.qa_chain = rag_chain.create_chain()
            print("✅ Loaded existing knowledge base")
        else:
            print("❌ No existing knowledge base found. Please provide a document path.")
    
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
                for i, doc in enumerate(sources[:2], 1):
                    preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
                    response += f"   {i}. {preview}\n"
            
            return response
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def chat(self):
        """Start the interactive chat session"""
        print("\n" + "="*60)
        print("🚀 RAG Terminal Chatbot")
        print("="*60)
        print("💡 Ask questions about your documents")
        print("💡 Type 'quit', 'exit', or 'bye' to end the session")
        print("="*60 + "\n")
        
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
    import sys
    
    if len(sys.argv) > 1:
        knowledge_base_path = sys.argv[1]
        if not os.path.exists(knowledge_base_path):
            print(f"❌ File not found: {knowledge_base_path}")
            return
    else:
        knowledge_base_path = None
    
    try:
        chatbot = TerminalRAGChatbot(knowledge_base_path)
        chatbot.chat()
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {str(e)}")

if __name__ == "__main__":
    main()
