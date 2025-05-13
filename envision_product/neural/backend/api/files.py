from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import List
from pydantic import BaseModel
import os
import logging

from services.file_service import FileService

router = APIRouter()
logger = logging.getLogger(__name__)

class FileInfo(BaseModel):
    file_id: str
    filename: str
    size: int
    upload_time: str
    content_type: str

class FileList(BaseModel):
    files: List[FileInfo]

# Dependency to get FileService instance
def get_file_service():
    return FileService()

@router.get("/", response_model=FileList)
async def list_files(file_service: FileService = Depends(get_file_service)):
    """List all uploaded files."""
    files = file_service.list_files()
    return {"files": files}

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    file_service: FileService = Depends(get_file_service)
):
    """Upload a new file."""
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    try:
        file_id = await file_service.save_file(file)
        return {
            "status": "success",
            "file_id": file_id,
            "filename": file.filename,
            "content_type": file.content_type
        }
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@router.get("/{file_id}")
async def get_file(
    file_id: str,
    file_service: FileService = Depends(get_file_service)
):
    """Download a file by ID."""
    file_path = file_service.get_file_path(file_id)
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File with ID {file_id} not found")
    
    # Get metadata to determine filename
    files = file_service.list_files()
    file_info = next((f for f in files if f.get("file_id") == file_id), None)
    
    if not file_info:
        raise HTTPException(status_code=404, detail=f"File metadata for ID {file_id} not found")
    
    return FileResponse(
        file_path,
        filename=file_info.get("filename", f"file_{file_id}"),
        media_type=file_info.get("content_type", "application/octet-stream")
    )

@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    file_service: FileService = Depends(get_file_service)
):
    """Delete a file by ID."""
    if not file_service.delete_file(file_id):
        raise HTTPException(status_code=404, detail=f"File with ID {file_id} not found or could not be deleted")
    
    return {"status": "success", "message": f"File {file_id} deleted successfully"} 