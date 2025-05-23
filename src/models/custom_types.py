from __future__ import annotations

import os
from typing import Any, Optional

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
    def __init__(self, repositories: dict[str, RepositoryConfig], environment_variables: dict[str, str]) -> None:
        self._repositories: dict[str, RepositoryConfig] = repositories
        self._environment_variables: dict[str, str] = environment_variables

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

        repositories: dict[str, RepositoryConfig] = {
            repository_name: RepositoryConfig(
                name=repository_config["name"],
                environment_variables=repository_config["environment_variables"],
                url=repository_config["url"],
            )
            for repository_name, repository_config in config["repositories"].items()
        }
        environment_variables: dict[str, str] = {
            "GITHUB_CLIENT_ID": os.getenv("GITHUB_CLIENT_ID"),
            "GITHUB_CLIENT_SECRET": os.getenv("GITHUB_CLIENT_SECRET"),
            "REDIRECT_URI": os.getenv("REDIRECT_URI"),
        }

        return Config(repositories=repositories, environment_variables=environment_variables)

    def update(self, repository_name: str, repository_config: RepositoryConfig) -> RepositoryConfig:
        self._repositories[repository_name] = repository_config

        self._save_to_file()

        return self._repositories[repository_name]

    @property
    def repositories(self) -> dict[str, RepositoryConfig]:
        return self._repositories

    @property
    def environment_variables(self) -> dict[str, str]:
        return self._environment_variables

    def add_repository_config(self, repository_name: str, repository_config: RepositoryConfig) -> None:
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


class URL:
    def __init__(self, path: str, params: Optional[dict[str, Any]] = None) -> None:
        self.path: str = path
        self.params: Optional[dict[str, Any]] = params if len(params) else None

    def __str__(self) -> str:
        combined_path: str = self.path

        if self.params:
            combined_path += "?" + "?".join(f"{key}={value}" for key, value in self.params.items())

        return combined_path


class AccessToken:
    def __init__(self, access_token: Optional[str] = None) -> None:
        self._access_token: Optional[str] = access_token

    def set(self, access_token: str) -> None:
        self._access_token = access_token

    def reset(self) -> None:
        self._access_token = None

    def __str__(self) -> str:
        return str(self._access_token)

    def __bool__(self) -> bool:
        return bool(self._access_token)
