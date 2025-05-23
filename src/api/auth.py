import urllib.parse
from http import HTTPStatus

import requests
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from src.core.helper import config, combine_url_and_params, access_token

router: APIRouter = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login", status_code=HTTPStatus.PERMANENT_REDIRECT)
async def login_with_github() -> RedirectResponse:
    github_auth_url: str = combine_url_and_params(
        path="https://github.com/login/oauth/authorize",
        params={
            "client_id": config.environment_variables["GITHUB_CLIENT_ID"],
            "scope": "repo user",
        },
    )

    return RedirectResponse(status_code=HTTPStatus.PERMANENT_REDIRECT, url=github_auth_url)


@router.get("/callback", status_code=HTTPStatus.PERMANENT_REDIRECT)
async def github_callback(code: str) -> RedirectResponse:
    token_response: requests.Response = requests.post(
        url="https://github.com/login/oauth/access_token",
        data={
            "client_id": config.environment_variables["GITHUB_CLIENT_ID"],
            "client_secret": config.environment_variables["GITHUB_CLIENT_SECRET"],
            "redirect_uri": "https://75ea-2001-a61-3066-7d01-ac34-e734-3c1f-9a87.ngrok-free.app/api/auth/callback/redirect",
            "code": code,
        },
    )
    token_data: dict[str, str] = {
        key: urllib.parse.unquote(value)
        for key, value in map(lambda entry: entry.split("="), token_response.text.split("&"))
    }
    access_token.set(token_data["access_token"])

    return RedirectResponse(
        status_code=HTTPStatus.PERMANENT_REDIRECT,
        url=config.environment_variables["REDIRECT_URI"],
    )


@router.get("/callback/redirect", status_code=HTTPStatus.PERMANENT_REDIRECT)
async def redirect() -> RedirectResponse:
    return RedirectResponse(status_code=HTTPStatus.PERMANENT_REDIRECT, url=config.environment_variables["REDIRECT_URI"])


@router.post("/logout", status_code=HTTPStatus.OK)
async def logout() -> None:
    access_token.reset()
