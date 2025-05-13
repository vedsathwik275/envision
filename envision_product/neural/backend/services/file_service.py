#!/usr/bin/env python3
import os
import shutil
import uuid
from datetime import datetime
from fastapi import UploadFile, HTTPException
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from config.settings import settings

class FileService:
    def __init__(self, storage_path: str = "data/uploads"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.storage_path / "metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load file metadata from JSON file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"files": {}}
        return {"files": {}}
    
    def _save_metadata(self):
        """Save current metadata to JSON file"""
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f, indent=2)
    
    async def save_file(self, file: UploadFile) -> str:
        """Save an uploaded file and return its ID
        
        Args:
            file: The uploaded file
            
        Returns:
            str: Unique file ID
        """
        # Generate a unique file ID
        file_id = str(uuid.uuid4())
        
        # Create file path
        file_path = self.storage_path / file_id
        
        # Save the file
        with open(file_path, "wb") as f:
            # Read file in chunks to handle large files
            chunk_size = 1024 * 1024  # 1MB chunks
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Check if file is too large (100MB limit)
        max_size = 100 * 1024 * 1024
        if file_size > max_size:
            os.remove(file_path)
            raise ValueError(f"File too large. Maximum size is 100MB.")
        
        # Store metadata
        self.metadata["files"][file_id] = {
            "file_id": file_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file_size,
            "upload_time": datetime.now().isoformat(),
            "path": str(file_path)
        }
        
        self._save_metadata()
        return file_id
    
    def get_file_path(self, file_id: str) -> Optional[str]:
        """Get the file path for a given file ID
        
        Args:
            file_id: The file ID
            
        Returns:
            str: Path to the file or None if not found
        """
        if file_id not in self.metadata["files"]:
            return None
        
        return self.metadata["files"][file_id]["path"]
    
    def list_files(self) -> List[Dict]:
        """List all uploaded files
        
        Returns:
            List[Dict]: List of file metadata
        """
        return [
            {
                "file_id": file_id,
                "filename": metadata["filename"],
                "size": metadata["size"],
                "upload_time": metadata["upload_time"],
                "content_type": metadata["content_type"]
            }
            for file_id, metadata in self.metadata["files"].items()
        ]
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file by its ID
        
        Args:
            file_id: The file ID
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        if file_id not in self.metadata["files"]:
            return False
        
        file_path = self.metadata["files"][file_id]["path"]
        try:
            os.remove(file_path)
            del self.metadata["files"][file_id]
            self._save_metadata()
            return True
        except:
            return False 