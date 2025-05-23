from fastapi import APIRouter

from .config import router as config_router
from .deployment import router as deployment_router
from .health import router as health_router
from .auth import router as auth_router
from .status import router as status_router

router: APIRouter = APIRouter(prefix="/api")
router.include_router(health_router)
router.include_router(config_router)
router.include_router(deployment_router)
router.include_router(status_router)
router.include_router(auth_router)

__all__ = ["router"]
