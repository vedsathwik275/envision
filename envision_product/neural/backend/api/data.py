#!/usr/bin/env python3
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import uuid
import os
import pandas as pd
from datetime import datetime
import logging

from services.file_service import FileService
from services.data_processor import DataProcessor
from config.settings import settings
from pydantic import BaseModel

router = APIRouter()
file_service = FileService()
data_processor = DataProcessor()
logger = logging.getLogger(__name__)

class PreviewResponse(BaseModel):
    file_id: str
    total_rows: int
    total_columns: int
    sample_rows: list
    column_info: Dict[str, Any]
    missing_data_summary: Optional[Dict[str, Any]] = None

class ProcessRequest(BaseModel):
    file_id: str
    options: Optional[Dict[str, Any]] = None

# Dependency to get service instances
def get_data_processor():
    return DataProcessor()

def get_file_service():
    return FileService()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Upload a CSV file for neural network training.
    The file will be validated and a preview will be generated.
    """
    # Validate file extension
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")
    
    try:
        # Save file to storage
        file_id = str(uuid.uuid4())
        file_path = await file_service.save_file(file, file_id)
        
        # Generate preview in background
        if background_tasks:
            background_tasks.add_task(data_processor.generate_preview, file_id, file_path)
        else:
            # For immediate preview
            preview = data_processor.generate_preview(file_id, file_path)
        
        return {
            "status": "success",
            "file_id": file_id,
            "filename": file.filename,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@router.get("/preview/{file_id}", response_model=PreviewResponse)
async def get_data_preview(
    file_id: str,
    data_processor: DataProcessor = Depends(get_data_processor),
    file_service: FileService = Depends(get_file_service)
):
    """Get a preview of data from a file."""
    # Check if file exists
    file_path = file_service.get_file_path(file_id)
    if not file_path:
        raise HTTPException(status_code=404, detail=f"File with ID {file_id} not found")
    
    # Get or generate preview
    preview = data_processor.get_preview(file_id, file_path)
    if not preview:
        raise HTTPException(status_code=500, detail=f"Failed to generate preview for file {file_id}")
    
    return preview

# @router.post("/process")
# async def process_data(
#     request: ProcessRequest,
#     data_processor: DataProcessor = Depends(get_data_processor),
#     file_service: FileService = Depends(get_file_service)
# ):
#     """Process a data file for further analysis."""
#     # Check if file exists
#     file_path = file_service.get_file_path(request.file_id)
#     if not file_path:
#         raise HTTPException(status_code=404, detail=f"File with ID {request.file_id} not found")
#     
#     try:
#         # Process the data file
#         # This could include operations like cleaning, transformation, feature engineering, etc.
#         # For now, we'll just return a preview as proof of concept
#         preview = data_processor.get_preview(request.file_id, file_path)
#         
#         return {
#             "status": "success",
#             "file_id": request.file_id,
#             "preview": preview
#         }
#     except Exception as e:
#         logger.error(f"Error processing data file {request.file_id}: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")

# @router.get("/")
# async def list_files():
#     """
#     List all uploaded files.
#     """
#     try:
#         files = file_service.list_files()
#         return {"files": files}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

# @router.delete("/{file_id}")
# async def delete_file(file_id: str):
#     """
#     Delete an uploaded file.
#     """
#     try:
#         result = file_service.delete_file(file_id)
#         if result:
#             return {"status": "success", "message": "File deleted successfully"}
#         else:
#             raise HTTPException(status_code=404, detail="File not found")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}") 