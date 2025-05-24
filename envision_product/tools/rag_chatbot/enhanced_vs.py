from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.llms import OpenAI
import os
from typing import List, Dict, Any
import numpy as np

class AdvancedVectorStoreManager:
    def __init__(self, persist_directory="./chroma_db"):
        self.embeddings = OpenAIEmbeddings()
        self.persist_directory = persist_directory
        self.llm = OpenAI(temperature=0.3)
        
    def create_vectorstore_with_metadata(self, texts):
        """Create vector store with enhanced metadata indexing"""
        vectorstore = Chroma.from_documents(
            documents=texts,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        vectorstore.persist()
        return vectorstore
    
    def create_hybrid_retriever(self, vectorstore, texts):
        """Create hybrid retriever combining vector search and BM25"""
        # Vector-based retriever
        vector_retriever = vectorstore.as_retriever(
            search_kwargs={"k": 6, "fetch_k": 20}
        )
        
        # BM25 retriever for keyword matching
        bm25_retriever = BM25Retriever.from_documents(texts)
        bm25_retriever.k = 6
        
        # Ensemble retriever combining both
        ensemble_retriever = EnsembleRetriever(
            retrievers=[vector_retriever, bm25_retriever],
            weights=[0.7, 0.3]  # Favor vector search slightly
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
    
    def create_advanced_retriever(self, vectorstore, texts, retriever_type="hybrid"):
        """Create advanced retriever based on type"""
        if retriever_type == "hybrid":
            return self.create_hybrid_retriever(vectorstore, texts)
        elif retriever_type == "multi_query":
            return self.create_multi_query_retriever(vectorstore)
        elif retriever_type == "compression":
            base_retriever = vectorstore.as_retriever(search_kwargs={"k": 8})
            return self.create_contextual_compression_retriever(base_retriever)
        elif retriever_type == "advanced_hybrid":
            # Combine multiple techniques
            hybrid_retriever = self.create_hybrid_retriever(vectorstore, texts)
            return self.create_contextual_compression_retriever(hybrid_retriever)
        else:
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
                embedding=self.embeddings
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
                bm25_docs = self.bm25_retriever.get_relevant_documents(query)
                
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
                for doc in bm25_docs[:k*2]:
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
        if os.path.exists(self.persist_directory):
            vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            return vectorstore
        return None
    
    def get_retrieval_statistics(self, vectorstore):
        """Get statistics about the vector store"""
        try:
            # Try to get collection info
            collection = vectorstore._collection
            count = collection.count()
            
            return {
                'total_documents': count,
                'embedding_dimension': len(self.embeddings.embed_query("test")),
                'storage_path': self.persist_directory
            }
        except:
            return {
                'total_documents': 'Unknown',
                'embedding_dimension': len(self.embeddings.embed_query("test")),
                'storage_path': self.persist_directory
            }