from http import HTTPStatus

from docker.models.containers import Container
from fastapi import APIRouter

from src.core.helper import get_all_containers, find_container
from src.models.custom_types import ContainerInfo
from src.models.responses import GetAllStatusResponse, ContainerStatusResponse

router: APIRouter = APIRouter(prefix="/status", tags=["status"])


@router.get("", status_code=HTTPStatus.OK, response_model=GetAllStatusResponse)
def get_status() -> GetAllStatusResponse:
    all_status: dict[str, ContainerInfo] = {}

    for container in get_all_containers():
        all_status[container.name] = ContainerInfo(
            id=container.id,
            name=container.name,
            status=container.status
        )

    return GetAllStatusResponse(status=all_status)


@router.get("/{repository_name}", status_code=HTTPStatus.OK, response_model=ContainerStatusResponse)
def get_status(repository_name: str) -> ContainerStatusResponse:
    container: Container = find_container(repository_name)
    container_info: ContainerInfo = ContainerInfo(
        id=container.id,
        name=container.name,
        status=container.status
    )

    return ContainerStatusResponse(status=container_info)
