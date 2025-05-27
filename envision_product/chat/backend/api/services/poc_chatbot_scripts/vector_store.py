from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import os

class VectorStoreManager:
    def __init__(self, persist_directory="./chroma_db"):
        self.embeddings = OpenAIEmbeddings()
        self.persist_directory = persist_directory
        
    def create_vectorstore(self, texts):
        """Create vector store from document chunks"""
        vectorstore = Chroma.from_documents(
            documents=texts,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        vectorstore.persist()
        return vectorstore
    
    def load_vectorstore(self):
        """Load existing vector store"""
        if os.path.exists(self.persist_directory):
            vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            return vectorstore
        return None
    
    def search_similar(self, vectorstore, query, k=3):
        """Search for similar documents"""
        docs = vectorstore.similarity_search(query, k=k)
        return docs
