from fastapi import APIRouter

from app.api.analysis_routes import router as analysis_router
from app.api.detection_routes import router as detection_router
from app.api.files_routes import router as files_router
from app.api.history_routes import router as history_router
from app.api.model_weight_routes import router as model_weight_router
from app.api.settings_routes import router as settings_router
from app.api.system_routes import router as system_router

router = APIRouter()
router.include_router(system_router)
router.include_router(history_router)
router.include_router(settings_router)
router.include_router(detection_router)
router.include_router(files_router)
router.include_router(model_weight_router)
router.include_router(analysis_router)
