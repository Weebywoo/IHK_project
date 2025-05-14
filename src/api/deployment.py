from http import HTTPStatus

from docker.models.containers import Container
from docker.models.images import Image
from fastapi import APIRouter

from src.core.helper import (
    clone_repository,
    build_image,
    remove_repository,
    deploy_image,
    config,
    find_container,
    find_new_port,
)
from src.models.custom_types import RepositoryConfig
from src.models.requests import CreateRepositoryRequest

router: APIRouter = APIRouter(prefix="/deployment", tags=["deployment"])


@router.post("/create/{repository_name}", status_code=HTTPStatus.CREATED)
async def create_deployment(repository_name: str, create_repository_request: CreateRepositoryRequest) -> None:
    ports: dict[str, int] = {}

    for port in create_repository_request.ports:
        external_port: int | None = find_new_port()

        if external_port:
            ports[port] = external_port

    repository_config: RepositoryConfig = RepositoryConfig(
        name=repository_name, url=create_repository_request.url, secrets=create_repository_request.secrets, ports=ports
    )

    config.add(repository_name, repository_config)

    await trigger_deployment(repository_config.name)


@router.delete("/remove/{repository_name}", status_code=HTTPStatus.NO_CONTENT)
async def remove_deployment(repository_name: str) -> None:
    container: Container = find_container(repository_name)

    if container:
        if container.status == "running":
            container.stop()

        container.remove()

    config.remove_repository_config(repository_name)


@router.post("/trigger/{repository_name}", status_code=HTTPStatus.OK)
async def trigger_deployment(repository_name: str) -> None:
    repository_config: RepositoryConfig = config.get(repository_name)
    path: str = clone_repository(str(repository_config.url), repository_config.name)
    image: Image = build_image(path)

    remove_repository(path)
    deploy_image(repository_config.name, repository_config.secrets, repository_config.ports, image)


@router.post("/stop/{repository_name}", status_code=HTTPStatus.OK)
async def stop_container(repository_name: str) -> None:
    container: Container = find_container(repository_name)

    if container and container.status == "running":
        container.stop()


@router.post("/start/{repository_name}", status_code=HTTPStatus.OK)
async def start_container(repository_name: str) -> None:
    container: Container = find_container(repository_name)

    if container and container.status == "exited":
        container.start()
