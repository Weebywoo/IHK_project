from http import HTTPStatus

from fastapi import APIRouter

from src.core.helper import (
    config,
)
from src.models.custom_types import RepositoryConfig
from src.models.requests import RepositoryConfigUpdateRequest
from src.models.responses import RepositoryConfigGetResponse, RepositoryConfigUpdateResponse

router: APIRouter = APIRouter(prefix="/config", tags=["config"])


@router.get("/{repository_name}", status_code=HTTPStatus.OK, response_model=RepositoryConfigGetResponse)
async def get_config(repository_name: str) -> RepositoryConfigGetResponse:
    return RepositoryConfigGetResponse(config=config.get(repository_name))


@router.put("/update/{repository_name}", status_code=HTTPStatus.OK, response_model=RepositoryConfigUpdateResponse)
async def update_config(
    repository_name: str, repository_config_update_request: RepositoryConfigUpdateRequest
) -> RepositoryConfigUpdateResponse:
    repository_config: RepositoryConfig = config.update(
        repository_name,
        RepositoryConfig(
            name=repository_config_update_request.name,
            secrets=repository_config_update_request.secrets,
            url=repository_config_update_request.url,
            ports=repository_config_update_request.ports,
        ),
    )

    return RepositoryConfigUpdateResponse(config=repository_config)
