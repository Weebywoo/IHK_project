import os

import docker
import yaml
from docker import DockerClient
from docker.models.containers import Container
from docker.models.images import Image
from git import Repo
from yaml import Loader

from src.models.custom_types import Config, occupied_ports, base_port

docker_client: DockerClient = docker.from_env()


def load_config() -> Config:
    with open("config.yaml") as config_file:
        return yaml.load(config_file, Loader)


config: Config = load_config()


def find_new_port() -> int | None:
    for port in range(base_port, 10000, 1):
        if port not in occupied_ports:
            return port

    return None


def clone_repository(repository_url: str, repository_name: str) -> str:
    path: str = "./repositories/" + repository_name

    Repo.clone_from(url=repository_url, to_path=path)

    return path


def build_image(path: str) -> Image:
    repository_name: str = path.split("/")[-1].split(".")[0]

    return docker_client.images.build(path=path, tag=repository_name, rm=True)[0]


def remove_repository(path: str) -> None:
    os.rmdir(path)


def get_all_containers() -> list[Container]:
    return docker_client.containers.list()


def find_container(repository_name: str) -> Container | None:
    for container in get_all_containers():
        if container.name == repository_name:
            return container

    return None


def deploy_image(repository_name: str, repository_secrets: dict[str, str], ports: dict[str, int], image: Image) -> None:
    container: Container = find_container(repository_name)

    if container:
        if container.status == "running":
            container.stop()

        container.remove()

    docker_client.containers.run(
        image,
        name=repository_name,
        detach=True,
        remove=True,
        network="host",
        environment=repository_secrets,
        ports=ports,
    )
