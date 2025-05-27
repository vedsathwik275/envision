from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.llms import OpenAI
import os
from typing import List, Dict, Any, Optional
import numpy as np
import pickle
from pathlib import Path

class AdvancedVectorStoreManager:
    def __init__(self, persist_directory="./chroma_db"):
        self.embeddings = OpenAIEmbeddings()
        self.persist_directory = Path(persist_directory)
        self.llm = OpenAI(temperature=0.3)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
    def _get_bm25_retriever_path(self) -> Path:
        """Helper to get the standardized path for the BM25 retriever pickle file."""
        return self.persist_directory / "bm25_retriever.pkl"

    def create_vectorstore_with_metadata(self, texts):
        """Create vector store with enhanced metadata indexing"""
        vectorstore = Chroma.from_documents(
            documents=texts,
            embedding=self.embeddings,
            persist_directory=str(self.persist_directory),
            collection_metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        vectorstore.persist()
        return vectorstore
    
    def create_hybrid_retriever(self, vectorstore, texts: Optional[List[Any]], persist_bm25_if_creating: bool = False):
        """Create hybrid retriever combining vector search and BM25.
        If texts are provided, BM25Retriever is built. If persist_bm25_if_creating is True, it's saved.
        If texts are not provided, BM25Retriever is loaded from disk.
        """
        vector_retriever = vectorstore.as_retriever(
            search_kwargs={"k": 6}
        )
        
        bm25_retriever_path = self._get_bm25_retriever_path()
        bm25_retriever = None

        if texts: # Typically during initial processing / setup
            print(f"Building BM25Retriever from {len(texts)} documents...")
            bm25_retriever = BM25Retriever.from_documents(texts)
            bm25_retriever.k = 6 # Set k for BM25 as well
            if persist_bm25_if_creating:
                try:
                    with open(bm25_retriever_path, "wb") as f:
                        pickle.dump(bm25_retriever, f)
                    print(f"BM25Retriever persisted to {bm25_retriever_path}")
                except Exception as e:
                    print(f"⚠️ Error persisting BM25Retriever to {bm25_retriever_path}: {e}")
                    # Decide if this should be a fatal error for setup
        elif bm25_retriever_path.exists(): # Typically during loading existing KB
            print(f"Loading BM25Retriever from {bm25_retriever_path}...")
            try:
                with open(bm25_retriever_path, "rb") as f:
                    bm25_retriever = pickle.load(f)
                print("BM25Retriever loaded successfully.")
            except Exception as e:
                print(f"❌ Error loading BM25Retriever from {bm25_retriever_path}: {e}")
                raise # Re-raise the exception as loading BM25 is critical here
        else:
            # This case means no texts to build BM25 and no persisted file to load.
            error_msg = f"BM25Retriever cannot be created: No texts provided and no persisted file found at {bm25_retriever_path}."
            print(f"❌ {error_msg}")
            raise FileNotFoundError(error_msg)

        if not bm25_retriever:
             # This should ideally be caught by the logic above, but as a safeguard:
            critical_error_msg = "BM25Retriever is None after creation/loading attempt. This should not happen."
            print(f"CRITICAL ERROR: {critical_error_msg}")
            raise ValueError(critical_error_msg)
        
        ensemble_retriever = EnsembleRetriever(
            retrievers=[vector_retriever, bm25_retriever],
            weights=[0.7, 0.3]  
        )
        
        return ensemble_retriever
    
    def create_multi_query_retriever(self, vectorstore):
        """Create multi-query retriever for query expansion"""
        base_retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
        
        multi_query_retriever = MultiQueryRetriever.from_llm(
            retriever=base_retriever,
            llm=self.llm
        )
        
        return multi_query_retriever
    
    def create_contextual_compression_retriever(self, base_retriever):
        """Create retriever with contextual compression"""
        compressor = LLMChainExtractor.from_llm(self.llm)
        
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=base_retriever
        )
        
        return compression_retriever
    
    def create_advanced_retriever(self, vectorstore, texts: Optional[List[Any]], retriever_type="hybrid", persist_bm25_if_creating: bool = False):
        """Create advanced retriever based on type.
        Passes persist_bm25_if_creating to hybrid retriever creation.
        """
        if retriever_type == "hybrid":
            return self.create_hybrid_retriever(vectorstore, texts, persist_bm25_if_creating=persist_bm25_if_creating)
        elif retriever_type == "multi_query":
            return self.create_multi_query_retriever(vectorstore)
        elif retriever_type == "compression": # Typically built on another retriever
            base_retriever = vectorstore.as_retriever(search_kwargs={"k": 8})
            return self.create_contextual_compression_retriever(base_retriever)
        elif retriever_type == "advanced_hybrid":
            # For advanced_hybrid, BM25 is also created/loaded via create_hybrid_retriever
            hybrid_retriever = self.create_hybrid_retriever(vectorstore, texts, persist_bm25_if_creating=persist_bm25_if_creating)
            # Then compression is added on top
            return self.create_contextual_compression_retriever(hybrid_retriever)
        else: # Default to standard vector store retriever
            return vectorstore.as_retriever(search_kwargs={"k": 4})
    
    def search_with_filters(self, vectorstore, query, filters=None, k=3):
        """Search with metadata filters"""
        if filters:
            docs = vectorstore.similarity_search(query, k=k, filter=filters)
        else:
            docs = vectorstore.similarity_search_with_score(query, k=k)
        return docs
    
    def search_with_mmr(self, vectorstore, query, k=4, fetch_k=20):
        """Search using Maximal Marginal Relevance for diversity"""
        docs = vectorstore.max_marginal_relevance_search(
            query, k=k, fetch_k=fetch_k
        )
        return docs
    
    def analyze_retrieval_quality(self, vectorstore, test_queries: List[str]):
        """Analyze retrieval quality with test queries"""
        results = []
        
        for query in test_queries:
            # Get results with scores
            docs_with_scores = vectorstore.similarity_search_with_score(query, k=5)
            
            # Analyze score distribution
            scores = [score for _, score in docs_with_scores]
            
            # Check source diversity
            sources = set(doc.metadata.get('source_file', 'unknown') 
                         for doc, _ in docs_with_scores)
            
            results.append({
                'query': query,
                'num_results': len(docs_with_scores),
                'score_range': (min(scores), max(scores)) if scores else (0, 0),
                'avg_score': np.mean(scores) if scores else 0,
                'source_diversity': len(sources),
                'unique_sources': list(sources)
            })
        
        return results
    
    def optimize_chunk_overlap(self, documents, test_queries, overlap_ratios=[0.1, 0.2, 0.3]):
        """Test different chunk overlap ratios to find optimal setting"""
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        
        results = {}
        
        for ratio in overlap_ratios:
            chunk_size = 1000
            overlap = int(chunk_size * ratio)
            
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=overlap
            )
            
            test_chunks = splitter.split_documents(documents)
            test_vectorstore = Chroma.from_documents(
                documents=test_chunks,
                embedding=self.embeddings,
                # Note: For temporary stores like this, persisting might not be needed or desirable
                # persist_directory=str(self.persist_directory / f"temp_overlap_test_{ratio}") 
            )
            
            # Test retrieval quality
            quality_results = self.analyze_retrieval_quality(test_vectorstore, test_queries)
            avg_score = np.mean([r['avg_score'] for r in quality_results])
            avg_diversity = np.mean([r['source_diversity'] for r in quality_results])
            
            results[ratio] = {
                'avg_retrieval_score': avg_score,
                'avg_source_diversity': avg_diversity,
                'total_chunks': len(test_chunks)
            }
        
        return results
    
    def create_custom_retriever_with_reranking(self, vectorstore, texts):
        """Create custom retriever with re-ranking based on multiple factors"""
        class CustomRetriever:
            def __init__(self, vectorstore, bm25_retriever, embeddings):
                self.vectorstore = vectorstore
                self.bm25_retriever = bm25_retriever
                self.embeddings = embeddings
            
            def get_relevant_documents(self, query: str, k: int = 4):
                # Get more candidates from both retrievers
                vector_docs = self.vectorstore.similarity_search_with_score(query, k=k*2)
                bm25_docs_list = self.bm25_retriever.get_relevant_documents(query)
                
                # Combine and deduplicate
                all_docs = {}
                
                # Add vector search results with scores
                for doc, score in vector_docs:
                    doc_id = doc.metadata.get('chunk_id', str(hash(doc.page_content)))
                    all_docs[doc_id] = {
                        'doc': doc,
                        'vector_score': 1.0 - score,  # Convert distance to similarity
                        'bm25_score': 0.0
                    }
                
                # Add BM25 scores
                for doc in bm25_docs_list[:k*2]:
                    doc_id = doc.metadata.get('chunk_id', str(hash(doc.page_content)))
                    if doc_id in all_docs:
                        all_docs[doc_id]['bm25_score'] = 1.0  # Simple binary score
                    else:
                        all_docs[doc_id] = {
                            'doc': doc,
                            'vector_score': 0.0,
                            'bm25_score': 1.0
                        }
                
                # Re-rank based on combined score and metadata
                ranked_docs = []
                for doc_id, info in all_docs.items():
                    doc = info['doc']
                    
                    # Combined score
                    combined_score = (0.7 * info['vector_score'] + 0.3 * info['bm25_score'])
                    
                    # Boost score based on metadata
                    content_type = doc.metadata.get('content_type', 'general')
                    if content_type == 'summary':
                        combined_score *= 1.2
                    elif content_type == 'academic':
                        combined_score *= 1.1
                    
                    # Boost recent documents
                    mod_date = doc.metadata.get('modification_date', 0)
                    if mod_date > 1640995200:  # After 2022
                        combined_score *= 1.05
                    
                    ranked_docs.append((doc, combined_score))
                
                # Sort and return top k
                ranked_docs.sort(key=lambda x: x[1], reverse=True)
                return [doc for doc, _ in ranked_docs[:k]]
        
        # Create BM25 retriever
        bm25_retriever = BM25Retriever.from_documents(texts)
        
        return CustomRetriever(vectorstore, bm25_retriever, self.embeddings)
    
    def load_vectorstore(self):
        """Load existing vector store"""
        if self.persist_directory.exists(): # Check if directory itself exists
            # Chroma will try to load from this directory.
            # It will raise an error if the collection/db is not found or corrupted.
            try:
                print(f"Attempting to load Chroma vector store from: {self.persist_directory}")
                vectorstore = Chroma(
                    persist_directory=str(self.persist_directory),
                    embedding_function=self.embeddings
                )
                print("Chroma vector store loaded successfully.")
                return vectorstore
            except Exception as e:
                print(f"❌ Error loading Chroma vector store from {self.persist_directory}: {e}")
                # Depending on the error, it might indicate a corrupted store or other issues.
                # For now, re-raise to make it visible during KB loading.
                raise
        else:
            print(f"Vector store persist directory not found: {self.persist_directory}")
        return None
    
    def get_retrieval_statistics(self, vectorstore):
        """Get statistics about the vector store"""
        try:
            collection = vectorstore._collection
            count = collection.count()
            return {
                'total_documents': count,
                'embedding_dimension': len(self.embeddings.embed_query("test")),
                'storage_path': str(self.persist_directory)
            }
        except Exception as e:
            print(f"Error getting retrieval statistics: {e}")
            return {
                'total_documents': -1, # Indicate error or unknown
                'embedding_dimension': -1,
                'storage_path': str(self.persist_directory)
            }