import os
import json
from datetime import datetime
from pathlib import Path

class KnowledgeBaseManager:
    def __init__(self, base_directory="./knowledge_bases"):
        self.base_directory = base_directory
        self.ensure_base_directory()
    
    def ensure_base_directory(self):
        """Create base directory if it doesn't exist"""
        os.makedirs(self.base_directory, exist_ok=True)
    
    def create_knowledge_base(self, name, description=""):
        """Create a new knowledge base folder"""
        kb_path = os.path.join(self.base_directory, name)
        
        if os.path.exists(kb_path):
            raise ValueError(f"Knowledge base '{name}' already exists")
        
        # Create folder structure
        os.makedirs(kb_path)
        os.makedirs(os.path.join(kb_path, "documents"))
        os.makedirs(os.path.join(kb_path, "vector_store"))
        
        # Create metadata file
        metadata = {
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "document_count": 0,
            "chunk_count": 0
        }
        
        metadata_path = os.path.join(kb_path, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Created knowledge base: {name}")
        print(f"📁 Documents folder: {os.path.join(kb_path, 'documents')}")
        return kb_path
    
    def list_knowledge_bases(self):
        """List all available knowledge bases"""
        if not os.path.exists(self.base_directory):
            return []
        
        knowledge_bases = []
        for item in os.listdir(self.base_directory):
            kb_path = os.path.join(self.base_directory, item)
            if os.path.isdir(kb_path):
                metadata_path = os.path.join(kb_path, "metadata.json")
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    knowledge_bases.append(metadata)
        
        return knowledge_bases
    
    def get_knowledge_base_path(self, name):
        """Get the path to a knowledge base"""
        kb_path = os.path.join(self.base_directory, name)
        if not os.path.exists(kb_path):
            raise ValueError(f"Knowledge base '{name}' not found")
        return kb_path
    
    def get_documents_path(self, name):
        """Get the documents folder path for a knowledge base"""
        kb_path = self.get_knowledge_base_path(name)
        return os.path.join(kb_path, "documents")
    
    def get_vector_store_path(self, name):
        """Get the vector store path for a knowledge base"""
        kb_path = self.get_knowledge_base_path(name)
        return os.path.join(kb_path, "vector_store")
    
    def update_metadata(self, name, **updates):
        """Update knowledge base metadata"""
        kb_path = self.get_knowledge_base_path(name)
        metadata_path = os.path.join(kb_path, "metadata.json")
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        metadata.update(updates)
        metadata["last_updated"] = datetime.now().isoformat()
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
