from http import HTTPStatus

from docker.models.containers import Container
from fastapi import APIRouter

from src.core.helper import get_all_containers, find_container, config
from src.models.custom_types import ContainerInfo
from src.models.responses import GetAllStatusResponse, ContainerStatusResponse

router: APIRouter = APIRouter(prefix="/status", tags=["status"])


@router.get("", status_code=HTTPStatus.OK, response_model=GetAllStatusResponse)
def get_all_status() -> GetAllStatusResponse:
    all_status: dict[str, ContainerInfo] = {
        container.name: ContainerInfo(
            id=container.id,
            name=container.name,
            status=container.status,
            environment_variables=config.repositories[container.name].environment_variables,
            url=config.repositories[container.name].url,
        )
        for container in get_all_containers()
    }

    return GetAllStatusResponse(status=all_status)


@router.get("/{repository_name}", status_code=HTTPStatus.OK, response_model=ContainerStatusResponse)
def get_status(repository_name: str) -> ContainerStatusResponse:
    container: Container = find_container(repository_name)
    container_info: ContainerInfo = ContainerInfo(
        id=container.id,
        name=container.name,
        status=container.status,
        url=config.repositories[repository_name].url,
        environment_variables=config.repositories[repository_name].environment_variables,
    )

    return ContainerStatusResponse(status=container_info)
