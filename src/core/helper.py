import os
import shutil
import stat
from typing import Optional, Any

import docker
from docker import DockerClient
from docker.models.containers import Container
from docker.models.images import Image
from git import Repo

from src.models.custom_types import Config, occupied_ports, base_port, AccessToken

docker_client: DockerClient = docker.from_env()
config: Config = Config.load()
access_token: AccessToken = AccessToken()


def combine_url_and_params(path: str, params: Optional[dict[str, Any]]) -> str:
    if params:
        path += "?" + "&".join(f"{key}={value}" for key, value in params.items())

    return path


def find_new_port() -> int | None:
    for port in range(base_port, 10000, 1):
        if port not in occupied_ports:
            return port

    return None


def clone_repository(repository_url: str, repository_name: str) -> None:
    if access_token:
        protocol, path = repository_url.split("://")
        repository_url = f"{protocol}://{access_token}@{path}"

    Repo.clone_from(url=repository_url, to_path="./repositories/" + repository_name)


def build_image(path: str) -> Image:
    repository_name: str = path.split("/")[-1].split(".")[0]

    return docker_client.images.build(path=path, tag=repository_name, rm=True)[0]


def readonly_handler(rm_func, path, exc_info):
    if issubclass(exc_info[0], PermissionError) and exc_info[1].winerror == 5:
        os.chmod(path, stat.S_IWRITE)

        return rm_func(path)

    raise exc_info[1]


def remove_repository(path: str) -> None:
    shutil.rmtree(path, onerror=readonly_handler)


def get_all_containers() -> list[Container]:
    return docker_client.containers.list(all=True)


def find_container(repository_name: str) -> Container | None:
    for container in get_all_containers():
        if container.name == repository_name:
            return container

    return None


def deploy_image(repository_name: str, environment_variables: dict[str, str], image: Image) -> None:
    container: Container | None = find_container(repository_name)

    if container:
        if container.status == "running":
            container.stop()

        container.remove()

    docker_client.containers.run(
        image,
        name=repository_name,
        detach=True,
        network="host",
        environment=environment_variables,
    )
