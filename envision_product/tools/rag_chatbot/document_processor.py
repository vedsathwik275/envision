from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader, PyPDFLoader, UnstructuredWordDocumentLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
import os
import glob
from pathlib import Path

class FolderDocumentProcessor:
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
    
    def get_document_files(self):
        """Get all supported document files from the folder"""
        files = []
        for ext in self.supported_extensions.keys():
            pattern = os.path.join(self.folder_path, f"**/*{ext}")
            files.extend(glob.glob(pattern, recursive=True))
        return files
    
    def load_document(self, file_path):
        """Load a single document based on its extension"""
        ext = Path(file_path).suffix.lower()
        
        if ext not in self.supported_extensions:
            print(f"⚠️  Unsupported file type: {file_path}")
            return []
        
        try:
            loader_class = self.supported_extensions[ext]
            
            # Special handling for CSV files
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
            
            # Add metadata about the source file
            for doc in documents:
                doc.metadata['source_file'] = os.path.basename(file_path)
                doc.metadata['file_path'] = file_path
                doc.metadata['file_type'] = ext
            
            print(f"✅ Loaded {len(documents)} records from {os.path.basename(file_path)}")
            return documents
            
        except Exception as e:
            print(f"❌ Error loading {file_path}: {str(e)}")
            return []
    
    def load_and_split_folder(self):
        """Load all documents from folder and split into chunks"""
        if not os.path.exists(self.folder_path):
            raise FileNotFoundError(f"Folder {self.folder_path} not found")
        
        all_documents = []
        files = self.get_document_files()
        
        if not files:
            raise ValueError(f"No supported documents found in {self.folder_path}")
        
        print(f"📂 Found {len(files)} document(s) in {self.folder_path}")
        
        for file_path in files:
            print(f"📄 Processing: {os.path.basename(file_path)}")
            documents = self.load_document(file_path)
            all_documents.extend(documents)
        
        if not all_documents:
            raise ValueError("No documents could be loaded successfully")
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )
        
        texts = text_splitter.split_documents(all_documents)
        print(f"✂️  Split {len(all_documents)} document(s) into {len(texts)} chunks")
        
        return texts
    
    def get_knowledge_base_info(self):
        """Get information about the knowledge base"""
        files = self.get_document_files()
        file_types = {}
        csv_files = []
        
        for file_path in files:
            ext = Path(file_path).suffix.lower()
            file_types[ext] = file_types.get(ext, 0) + 1
            
            if ext == '.csv':
                csv_files.append(os.path.basename(file_path))
        
        info = {
            'total_files': len(files),
            'file_types': file_types,
            'folder_path': self.folder_path
        }
        
        if csv_files:
            info['csv_files'] = csv_files
        
        return info
    
    def debug_file_detection(self):
        """Debug method to show what files are being detected"""
        files = self.get_document_files()
        print(f"\n🔍 Debug: Found {len(files)} files:")
        
        for file_path in files:
            ext = Path(file_path).suffix.lower()
            size = os.path.getsize(file_path)
            print(f"   📄 {os.path.basename(file_path)} ({ext}) - {size} bytes")
        
        return files