import os.path
from http import HTTPStatus

from docker.models.containers import Container
from docker.models.images import Image
from fastapi import APIRouter, HTTPException

from src.core.helper import (
    clone_repository,
    build_image,
    remove_repository,
    deploy_image,
    config,
    find_container,
)
from src.models.custom_types import RepositoryConfig
from src.models.requests import CreateRepositoryRequest, GithubWebhookRequest

router: APIRouter = APIRouter(prefix="/deployment", tags=["deployment"])


@router.post("/create/{repository_name}", status_code=HTTPStatus.CREATED)
async def create_deployment(repository_name: str, create_repository_request: CreateRepositoryRequest) -> None:
    repository_config: RepositoryConfig = RepositoryConfig(
        name=repository_name,
        url=create_repository_request.url,
        environment_variables=create_repository_request.environment_variables,
    )

    config.add(repository_name, repository_config)

    await trigger_deployment(repository_name)


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
    path: str = "./repositories/" + repository_name
    repository_config: RepositoryConfig = config.repositories[repository_name]

    clone_repository(str(repository_config.url), repository_config.name)

    image: Image = build_image(path)

    remove_repository(path)

    deploy_image(repository_config.name, repository_config.environment_variables, image)



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


@router.post("/github", status_code=HTTPStatus.OK)
async def github_webhook_handler(github_webhook_request: GithubWebhookRequest) -> None:
    repository_name: str = github_webhook_request.repository.name

    if repository_name not in config.repositories:
        raise HTTPException(404, f"Could not find repository {repository_name} in config.")

    if github_webhook_request.repository.master_branch == "main":
        await trigger_deployment(repository_name)
