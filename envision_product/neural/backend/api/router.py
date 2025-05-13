from fastapi import APIRouter

from .files import router as files_router
from .data import router as data_router
from .models import router as models_router
from .predictions import router as predictions_router

router = APIRouter()

router.include_router(files_router, prefix="/files", tags=["files"])
router.include_router(data_router, prefix="/data", tags=["data"])
router.include_router(models_router, tags=["models"])
router.include_router(predictions_router, tags=["predictions"]) 