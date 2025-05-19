from __future__ import annotations

import yaml
from pydantic import BaseModel, Field, AliasChoices

occupied_ports: list[int] = []
base_port: int = 8000


class RepositoryConfig(BaseModel):
    name: str
    environment_variables: dict[str, str] = Field(
        serialization_alias="environmentVariables",
        validation_alias=AliasChoices("environmentVariables", "environment_variables"),
    )
    url: str


class Config:
    def __init__(self, repositories: dict[str, RepositoryConfig]) -> None:
        self._repositories: dict[str, RepositoryConfig] = repositories

    @staticmethod
    def load() -> Config:
        with open("config.yaml") as config_file:
            config: dict | None = yaml.safe_load(config_file)

        if not config:
            config = {}

        if "repositories" not in config:
            config["repositories"] = {}

        if not config["repositories"]:
            config["repositories"] = {}

        return Config(
            repositories={
                repository_name: RepositoryConfig(
                    name=repository_config["name"],
                    environment_variables=repository_config["environment_variables"],
                    url=repository_config["url"],
                )
                for repository_name, repository_config in config["repositories"].items()
            }
        )

    def update(self, repository_name: str, repository_config: RepositoryConfig) -> RepositoryConfig:
        self._repositories[repository_name] = repository_config

        self._save_to_file()

        return self._repositories[repository_name]

    @property
    def repositories(self) -> dict[str, RepositoryConfig]:
        return self._repositories

    def add(self, repository_name: str, repository_config: RepositoryConfig) -> None:
        if repository_name not in self._repositories:
            self._repositories[repository_name] = repository_config

        self._save_to_file()

    def remove_repository_config(self, repository_name: str) -> None:
        self._repositories.pop(repository_name)

        self._save_to_file()

    def _save_to_file(self) -> None:
        with open("config.yaml", "w") as config_file:
            yaml.dump(
                {
                    "repositories": {
                        repository_name: repository.model_dump()
                        for repository_name, repository in self._repositories.items()
                    }
                },
                config_file,
            )


class ContainerInfo(BaseModel):
    name: str
    id: str
    status: str
    url: str
    environment_variables: dict[str, str] = Field(
        serialization_alias="environmentVariables",
        validation_alias=AliasChoices("environmentVariables", "environment_variables"),
    )


class GithubRepository(BaseModel):
    name: str
    private: bool
    clone_url: str
    master_branch: str
