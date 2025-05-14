from typing import Annotated, TypeAlias, Literal

import yaml
from pydantic import BaseModel, AfterValidator, HttpUrl


def check_specific_hosts(url: HttpUrl) -> HttpUrl:
    if url.host == "www.github.com":
        return url

    raise ValueError(f"{url} is not in the list of accepted hosts")


ValidUrl: TypeAlias = Annotated[HttpUrl, AfterValidator(check_specific_hosts)]
occupied_ports: list[int] = []
base_port: int = 8000


class RepositoryConfig(BaseModel):
    name: str
    secrets: dict[str, str]
    url: ValidUrl
    ports: dict[str, int]


class Config(BaseModel):
    _repositories: dict[str, RepositoryConfig]

    def update(self, repository_name: str, repository_config: RepositoryConfig) -> RepositoryConfig:
        self._repositories[repository_name] = repository_config

        self._save_to_file()

        return self._repositories[repository_name]

    def get(self, repository_name: str) -> RepositoryConfig:
        return self._repositories[repository_name]

    def add(self, repository_name: str, repository_config: RepositoryConfig) -> None:
        if repository_name not in self._repositories:
            self._repositories[repository_name] = repository_config

        self._save_to_file()

    def remove_repository_config(self, repository_name: str) -> None:
        self._repositories.pop(repository_name)

        self._save_to_file()

    def _save_to_file(self) -> None:
        with open("config.yaml") as config_file:
            yaml.dump(self.model_dump(), config_file)


class ContainerInfo(BaseModel):
    name: str
    id: str
    status: str
