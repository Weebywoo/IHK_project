from pydantic import BaseModel

from src.models.custom_types import ValidUrl


class CreateRepositoryRequest(BaseModel):
    secrets: dict[str, str]
    url: ValidUrl
    ports: list[str]


class RepositoryConfigUpdateRequest(BaseModel):
    name: str
    secrets: dict[str, str]
    url: ValidUrl
    ports: dict[str, int]
