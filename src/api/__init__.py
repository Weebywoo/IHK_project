from fastapi import APIRouter

from .health import router as health_router

router: APIRouter = APIRouter(prefix="/api")
router.include_router(health_router)

__all__ = ["router"]
