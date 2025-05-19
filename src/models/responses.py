from typing import Literal

from pydantic import BaseModel

from src.models.custom_types import RepositoryConfig, ContainerInfo


class HealthResponse(BaseModel):
    status: Literal["ok"]


class RepositoryConfigGetResponse(BaseModel):
    config: RepositoryConfig


class RepositoryConfigUpdateResponse(BaseModel):
    config: RepositoryConfig


class ContainerStatusResponse(BaseModel):
    status: ContainerInfo


class GetAllStatusResponse(BaseModel):
    status: dict[str, ContainerInfo]
