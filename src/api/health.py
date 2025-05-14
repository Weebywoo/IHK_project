from http import HTTPStatus

from fastapi import APIRouter

from src.models.responses import HealthResponse

router: APIRouter = APIRouter(prefix="/health", tags=["health"])


@router.get("/status", status_code=HTTPStatus.OK, response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok")
