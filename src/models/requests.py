from pydantic import BaseModel, Field, AliasChoices

from src.models.custom_types import GithubRepository


class CreateRepositoryRequest(BaseModel):
    environment_variables: dict[str, str] = Field(
        serialization_alias="environmentVariables",
        validation_alias=AliasChoices("environmentVariables", "environment_variables"),
    )
    url: str


class RepositoryConfigUpdateRequest(BaseModel):
    name: str
    environment_variables: dict[str, str] = Field(
        serialization_alias="environmentVariables",
        validation_alias=AliasChoices("environmentVariables", "environment_variables"),
    )
    url: str


class GithubWebhookRequest(BaseModel):
    repository: GithubRepository
