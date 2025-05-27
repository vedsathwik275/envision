from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader, PyPDFLoader, UnstructuredWordDocumentLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
import os
import glob
from pathlib import Path
import hashlib

class EnhancedDocumentProcessor:
    def __init__(self, folder_path, chunk_size=1000, chunk_overlap=200):
        self.folder_path = folder_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.supported_extensions = {
            '.txt': TextLoader,
            '.pdf': PyPDFLoader,
            '.docx': UnstructuredWordDocumentLoader,
            '.doc': UnstructuredWordDocumentLoader,
            '.csv': CSVLoader
        }
    
    def create_smart_text_splitter(self):
        """Create an intelligent text splitter"""
        return RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=[
                "\n\n\n",  # Paragraph breaks
                "\n\n",    # Double newlines
                "\n",      # Single newlines
                ". ",      # Sentence endings
                "! ",      # Exclamation endings
                "? ",      # Question endings
                "; ",      # Semicolons
                ", ",      # Commas
                " ",       # Spaces
                ""         # Character level
            ],
            keep_separator=True
        )
    
    def enhance_document_metadata(self, documents, file_path):
        """Add comprehensive metadata to documents"""
        file_stats = os.stat(file_path)
        file_hash = self.calculate_file_hash(file_path)
        
        enhanced_metadata = {
            'source_file': os.path.basename(file_path),
            'file_path': file_path,
            'file_type': Path(file_path).suffix.lower(),
            'file_size': file_stats.st_size,
            'creation_date': file_stats.st_ctime,
            'modification_date': file_stats.st_mtime,
            'file_hash': file_hash,
            'document_length': sum(len(doc.page_content) for doc in documents),
            'chunk_count': len(documents)
        }
        
        for i, doc in enumerate(documents):
            doc.metadata.update(enhanced_metadata)
            doc.metadata['chunk_index'] = i
            doc.metadata['chunk_id'] = f"{file_hash}_{i}"
            
            # Add content-based metadata
            doc.metadata['word_count'] = len(doc.page_content.split())
            doc.metadata['char_count'] = len(doc.page_content)
            
            # Detect content type heuristics
            content_lower = doc.page_content.lower()
            if any(keyword in content_lower for keyword in ['table', 'column', 'row', 'data']):
                doc.metadata['content_type'] = 'tabular'
            elif any(keyword in content_lower for keyword in ['abstract', 'introduction', 'conclusion']):
                doc.metadata['content_type'] = 'academic'
            elif any(keyword in content_lower for keyword in ['summary', 'overview', 'executive']):
                doc.metadata['content_type'] = 'summary'
            else:
                doc.metadata['content_type'] = 'general'
        
        return documents
    
    def calculate_file_hash(self, file_path):
        """Calculate file hash for deduplication"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def load_document_with_preprocessing(self, file_path):
        """Load document with enhanced preprocessing"""
        ext = Path(file_path).suffix.lower()
        
        if ext not in self.supported_extensions:
            print(f"⚠️  Unsupported file type: {file_path}")
            return []
        
        try:
            loader_class = self.supported_extensions[ext]
            
            # Enhanced CSV handling
            if ext == '.csv':
                loader = loader_class(
                    file_path=file_path,
                    csv_args={
                        "delimiter": ",",
                        "quotechar": '"',
                    }
                )
            else:
                loader = loader_class(file_path)
            
            documents = loader.load()
            
            # Preprocess content
            for doc in documents:
                doc.page_content = self.clean_content(doc.page_content)
            
            # Add enhanced metadata
            documents = self.enhance_document_metadata(documents, file_path)
            
            print(f"✅ Loaded and processed {len(documents)} chunks from {os.path.basename(file_path)}")
            return documents
            
        except Exception as e:
            print(f"❌ Error loading {file_path}: {str(e)}")
            return []
    
    def clean_content(self, content):
        """Clean and normalize content"""
        if not content:
            return content
        
        # Remove excessive whitespace
        content = ' '.join(content.split())
        
        # Fix common OCR/parsing issues
        content = content.replace('�', ' ')  # Remove replacement characters
        content = content.replace('\x00', ' ')  # Remove null bytes
        
        # Normalize quotes
        content = content.replace('"', '"').replace('"', '"')
        content = content.replace(''', "'").replace(''', "'")
        
        return content
    
    def load_and_split_folder_enhanced(self):
        """Enhanced folder processing with smart chunking"""
        if not os.path.exists(self.folder_path):
            raise FileNotFoundError(f"Folder {self.folder_path} not found")
        
        all_documents = []
        files = self.get_document_files()
        
        if not files:
            raise ValueError(f"No supported documents found in {self.folder_path}")
        
        print(f"📂 Processing {len(files)} document(s) from {self.folder_path}")
        
        # Track duplicates
        seen_hashes = set()
        
        for file_path in files:
            print(f"📄 Processing: {os.path.basename(file_path)}")
            documents = self.load_document_with_preprocessing(file_path)
            
            # Check for duplicates
            if documents:
                file_hash = documents[0].metadata.get('file_hash')
                if file_hash in seen_hashes:
                    print(f"⚠️  Skipping duplicate file: {os.path.basename(file_path)}")
                    continue
                seen_hashes.add(file_hash)
                
            all_documents.extend(documents)
        
        if not all_documents:
            raise ValueError("No documents could be loaded successfully")
        
        # Smart text splitting
        text_splitter = self.create_smart_text_splitter()
        texts = text_splitter.split_documents(all_documents)
        
        # Add chunk relationship metadata
        for i, chunk in enumerate(texts):
            chunk.metadata['global_chunk_index'] = i
            chunk.metadata['total_chunks'] = len(texts)
        
        print(f"✂️  Created {len(texts)} intelligent chunks from {len(all_documents)} documents")
        
        return texts
    
    def get_document_files(self):
        """Get all supported document files from the folder"""
        files = []
        for ext in self.supported_extensions.keys():
            pattern = os.path.join(self.folder_path, f"**/*{ext}")
            files.extend(glob.glob(pattern, recursive=True))
        return files
    
    def analyze_knowledge_base_quality(self, texts):
        """Analyze the quality and characteristics of the knowledge base"""
        if not texts:
            return {}
        
        total_content_length = sum(len(chunk.page_content) for chunk in texts)
        avg_chunk_size = total_content_length / len(texts)
        
        # Content type distribution
        content_types = {}
        file_types = {}
        
        for chunk in texts:
            content_type = chunk.metadata.get('content_type', 'unknown')
            file_type = chunk.metadata.get('file_type', 'unknown')
            
            content_types[content_type] = content_types.get(content_type, 0) + 1
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        unique_files = len(set(chunk.metadata.get('source_file', '') for chunk in texts))
        
        quality_metrics = {
            'total_chunks': len(texts),
            'total_content_length': total_content_length,
            'average_chunk_size': avg_chunk_size,
            'unique_source_files': unique_files,
            'content_type_distribution': content_types,
            'file_type_distribution': file_types,
            'recommendations': self.get_quality_recommendations(texts)
        }
        
        return quality_metrics
    
    def get_quality_recommendations(self, texts):
        """Generate recommendations for improving knowledge base quality"""
        recommendations = []
        
        if len(texts) < 10:
            recommendations.append("Consider adding more documents for better coverage")
        
        avg_size = sum(len(chunk.page_content) for chunk in texts) / len(texts)
        if avg_size < 200:
            recommendations.append("Chunks are quite small - consider increasing chunk_size")
        elif avg_size > 2000:
            recommendations.append("Chunks are large - consider decreasing chunk_size for better retrieval")
        
        unique_files = len(set(chunk.metadata.get('source_file', '') for chunk in texts))
        if unique_files < 3:
            recommendations.append("Limited source diversity - add documents from different sources")
        
        return recommendations